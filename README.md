# Azure Serverless Python Function to remove EXIF data from images

This repo will demonstrate how to deploy a serverless python function to Azure, and use this to automatically remove EXIF data from images as they land in a blob storage location.


## Development environment setup
This repo assumes a linux-based development environment. 

If none is available, consider using the [Azure Cloud Shell](https://docs.microsoft.com/en-gb/azure/cloud-shell/quickstart) or look into [WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

See [./dev_setup](./dev_setup) for how to set up the local development environment:
- Azure CLI
- Azure Functions Core Tools
- local Python environment

## Infrastructure provisioning
See [./infrastructure](./infrastructure) on how to use the Azure CLI to provision:
- Azure resource group
- Azure storage account
- Azure Function App resource on consumption plan

## Develop the python function locally
We will work with Azure Functions Core Tools from the command line. This example does not make use of any VScode extensions.

An example of the python function app code is available in the [./functionapp-py](./functionapp-py) folder. To use this code as is, create a `local.settings.json` file in that folder as described in step 2 below (not included in the repo because it is .gitignored), and then continue at step 5.

The following walks through the steps to create new functionapp code locally.

### 1. Prerequisites
Ensure that Azure Functions Core Tools is installed and an Azure Function App resource is available (complete the sections in [dev setup](dev_setup/readme.md) and [infrastructure setup](./infrastructure/readme.md)).

### 2. Initialise a new functionapp folder:
```sh
func init myfunctionapp-py
# -> choose 4. python
```

Review the files that have been created, and change into the new folder:
```sh
cd myfunctionapp-py
```

Update the `local.settings.json` file as follows:
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<connection-string-of-any-utility-storage-account, or same as next>",
    "STORAGE_CONN_STR":"<connection-string-of-storage-account created infrastructure setup>",
    "INPUT_PATH":"images/originals/",
    "OUTPUT_PATH":"images/no-exif/"
    }
}
```

### 3. Create a new function

```sh
func new 
# -> choose 1. Azure Blob Storage trigger, and name it (e.g. myRemoveExif)
```

### 4. Adapt the default function code:

Open the `function.json` config file within your new fuction folder, and edit the bindings as follows:
```
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "inimage",
      "type": "blobTrigger",
      "direction": "in",
      "path": "%INPUT_PATH%{name}",
      "connection": "STORAGE_CONN_STR"
    },
    {
      "name": "outimage",
      "type": "blob",
      "direction": "out",
      "path": "%OUTPUT_PATH%{name}",
      "connection": "STORAGE_CONN_STR"
    }
  ]
}
```

This code makes an objects available to our function (`inimage`) that we can read from (direction = `in`) and write to (direction = `out`).

Both objects point to a path in our linked storage, identified by the `INPUT_PATH`, `OUTPUT_PATH`, and `STORAGE_CONN_STR` that we specified as environment variables for the function app earlier in the `local.settings.json` file. 

The type `blobTrigger` ensures that we don't have to initiate a read from the function, but that it is initated by dropping a file into that location. 

Replace the `__init__.py` code within your new function with that shared in [./functionapp-py/removeExif](./functionapp-py/removeExif).

Lines of the format `logging.info(<msg>)` can be used to output additional log messages from within the function code for the local test. Once deployed (see step 6) these logs can also be reviewed from within the function monitoring pane in the Azure Portal.


### 5. Start the function locally and test it.

From within the functionapp folder (e.g. myfunctionapp-py)
```sh
func start
```

Using Azure Storage Explorer or the Storage Browser integrated into the Azure Portal, upload a pdf file to the `/images/originals/` folder in the storage account, and watch the terminal output for logs. 

On successful execution, navigate to the `/images/no-exif/` folder in the storage account and review the extracted page 1.

While running, changes can be made to the function code, and the function will automatically reload. 

Stop the function with a keyboard interrupt (`CTRL + C`).


### 6. Deploy the python function to the Azure Function App

The `--publish-local-settings` option ensures that the same environment variables as in our `local.settings.json` file are available in the deployed function app. Alternatively, the app settings can be configured and updated via the `Configuration` pane in the Azure Portal once the function is published. The `--build remote` option forces the upload of the requirements.txt file to the function app, and the installation of the required packages on the function app.
```
func azure functionapp publish $FUNCTION_APP_NAME --publish-local-settings --build remote
```

Test as before, by uploading a pdf to the input path at `/images/originals/`.

Review the logs of function execution by navigating to `Functions` > `your function` within the Azure Portal function app resource, and selecting the `Monitor` pane to review function invocations. The `Logs` tab on that pane connects to the log stream of the function execution.

### [Optional] 7. Edit the function settings

Navigate to the function app settings on the `Configuration` pane of the Azure Function App in the Azure Portal. 

- Update the OUTPUT_PATH to `images/myotheroutput/`

Click `Save`, and re-test.


## Further Reading
- [https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [https://github.com/Azure/azure-functions-python-worker/issues/832](https://github.com/Azure/azure-functions-python-worker/issues/832)
