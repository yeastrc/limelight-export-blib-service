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

__version__ = '1.0.0'
__spectr_get_scan_data_env_key__ = 'SPECTR_GET_SCAN_DATA_URL'
__webapp_port_env_key__ = 'WEBAPP_PORT'
__spectr_number_of_scans_to_request__ = 20
__proton_mass__ = 1.007276466621

# environmental variable name for the full path to the work dir
__workdir_env_key__ = 'APP_WORKDIR'

# environmental variable name for the full path to the final dir to place the blib file
__blib_dir_env_key__ = 'BLIB_DIR'

# how long (in seconds) to sleep between checking for new requests to process
__request_check_delay__ = 10

# array of dicts, each dict: {id: request id, data: the xml data of the request}
request_queue = []

# dict of:
#   request id : {
#       status: one of 'queued', 'error', or 'success',
#       message: file path if successful, error message otherwise
#   }
request_status_dict = {}
