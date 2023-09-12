import logging
import os

import azure.functions as func

from PIL import Image
#from io import BytesIO

def checkExif(filename):
    img = Image.open(filename)
    if img.getexif():
        logging.info(f"Image {filename} has exif data")
        logging.info(f"Exif data: {img.getexif()}")
    else:
        logging.info(f"Image {filename} has no exif data")
    img.close()


def main(inimage: func.InputStream, outimage: func.Out[func.InputStream]):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"path: {inimage.name}\n"
                 f"Name: {os.path.basename(inimage.name)}\n"
                 f"Blob Size: {inimage.length} bytes")
    
    filename = os.path.basename(inimage.name)

    # check file type
    if filename.split('.')[1] not in ['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG']:
        logging.info(f"File type not supported: {filename.split('.')[1]}")
        return

    # output filename
    outfilename = filename.split('.')[0] + '_noexif.' + filename.split('.')[1]

    # dowload file from input binding to function runtime local disk
    with open (f'/tmp/{filename}', 'wb') as localfile:
        localfile.write(inimage.read())

    # log existing exif data
    checkExif(f'/tmp/{filename}')

    # use PIL to remove exif data
    # https://stackoverflow.com/questions/43530148/how-to-remove-exif-data-from-images

    img = Image.open(f'/tmp/{filename}')

    # This should work for jpegs: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-saving
    #img.save(outfilename, 'JPEG', quality=100, exif=b'')
    #img.close()

    # This is more robust for various formats
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)
        
    image_without_exif.save(f'/tmp/{outfilename}')    # note default quality for jpg is 75, if this needs to be tweaked, 
                                            # then customise save function for different image formats

    image_without_exif.close()

    # double-check exif data has been removed
    checkExif(f'/tmp/{outfilename}')


    # write stream to outimage binding
    outfile = open(f'/tmp/{outfilename}', 'rb')
    outimage.set(outfile.read())

    # delete local file
    os.remove(f'/tmp/{filename}')
    os.remove(f'/tmp/{outfilename}')
