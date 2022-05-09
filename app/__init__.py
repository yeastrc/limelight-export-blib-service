"""Initialize values for use by this package"""

#   Copyright 2022 Michael Riffle
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os

__version__ = '1.0.0'

# environmental variable for the number of scans to process at a time from spectr
__spectr_batch_size_env_key__ = 'SPECTR_BATCH_SIZE'

# environmental variable name for the port to use for this web service
__webapp_port_env_key__ = 'WEBAPP_PORT'

# environmental variable name for URL to the spectr web service for retrieving scan data
__spectr_get_scan_data_env_key__ = 'SPECTR_GET_SCAN_DATA_URL'

# environmental variable name for the full path to the work dir
__workdir_env_key__ = 'APP_WORKDIR'

# environmental variable name for the full path to the final dir to place the blib file
__blib_dir_env_key__ = 'BLIB_DIR'

# environmental variable name for full path to BlibBuild and BlibFilter executables
__blib_build_executable_path_env_key__ = 'BLIB_BUILD_EXEC_PATH'
__blib_filter_executable_path_env_key__ = 'BLIB_FILTER_EXEC_PATH'

# environmental variable for whether or not to clean the working directory after each request
__clean_working_directory_env_key__ = 'APP_CLEAN_WORKDIR'

# how long (in seconds) to sleep between checking for new requests to process
__request_check_delay__ = 10

# array of dicts, each dict: {id: request id, data: the xml data of the request}
request_queue = []

# dict of:
#   request id : {
#       status: one of 'queued', 'processing', 'not found', 'success', 'error'
#       message: file path if successful, error message otherwise
#   }
request_status_dict = {}

# whether or not the request queue processing has been started up
request_queue_status = {'started': False}

# ensure all environmental variables are present
env_var_names = [
    __spectr_batch_size_env_key__,
    __webapp_port_env_key__,
    __spectr_get_scan_data_env_key__,
    __workdir_env_key__,
    __blib_dir_env_key__,
    __blib_build_executable_path_env_key__,
    __blib_filter_executable_path_env_key__
]

for env_var_name in env_var_names:
    if os.getenv(env_var_name) is None:
        raise ValueError('Missing environmental variable:', env_var_name)
