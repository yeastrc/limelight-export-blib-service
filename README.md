# limelight-export-blib-service
Python-based service for exporting blib files from Limelight. 

## Installation Instructions (using `docker-compose`)
Normally this service gets installed automatically when following our [installation instructions](https://limelight-ms.readthedocs.io/en/latest/administration.html)
for installing Limelight.

However, if you wish to install it separately (e.g., you are running Limelight not using our docker-based installation),
follow these directions.

1. Pull this repository to your local system: `git clone https://github.com/yeastrc/limelight-export-blib-service.git`
2. Copy `env-example` to `.env` (`cp env-example .env`). 
3. Edit `.env` and set the requested variables for your local system. See below for the list of items to configure.
4. Bring up the service with `docker-compose up --detach --build`

### Items in `.env` to Configure

- HOST_MACHINE_BLIB_DIR: The full path to a directory on the host machine where the final .blib files will be placed
- HOST_MACHINE_WORKDIR: The full path to a directory on the host machine that will be used as a working directory to generate the .blib file
- HOST_MACHINE_WEBAPP_PORT: The port on the host machine that will listen to requests to this service
- SPECTR_GET_SCAN_DATA_URL: URL to getScanDataFromScanNumbers_JSON spectr webservice. For example, `http://HOST:PORT/spectral_storage_get_data/query/getScanDataFromScanNumbers_JSON`
- UID: Optional, but recommended: The user id this service will run as. Defaults to 0 (root)
- GID: Optional, but recommended: The group id this service will run as. Defaults to 0 (root)
- SPECTR_BATCH_SIZE: The number of scans to request at a time from spectr. Optimally set to match spectr's configured maximum batch size
- APP_CLEAN_WORKDIR: One of:
   
  - `yes`: Always delete working directory after processing a request
  - `no`: Never delete a working directory after processing a request
  - `on success`: Delete working directory only after successfully processing a request
