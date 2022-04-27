"""Simple script to test functionality of app/ms2_lib"""

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
from app import __spectr_get_scan_data_env_key__, spectr_utils, ms2_lib
from dotenv import load_dotenv

# load values from .env into env
load_dotenv()

spectr_get_url = os.getenv('SPECTR_GET_SCAN_DATA_URL')
scan_number_list = os.getenv('TEST_SCAN_NUMBERS').strip('][').split(', ')
spectr_file_id = os.getenv('TEST_SPECTR_FILE_ID')
ms2_file_name = os.getenv('TEST_MS2_FILE_NAME')


def main():

    # set the env var needed to get data from spectr
    os.environ[__spectr_get_scan_data_env_key__] = spectr_get_url

    # do the work
    results = spectr_utils.get_scan_data_for_scan_numbers(spectr_file_id, scan_number_list)

    ms2_file = ms2_lib.initialize_ms2_file('.', ms2_file_name)

    for ms2_scan in results:
        ms2_lib.write_scan_to_ms2_file(ms2_file, ms2_scan.scan_number, ms2_scan.precursor_mz,
                                       ms2_scan.precursor_charge, ms2_scan.peak_list_mz,
                                       ms2_scan.peak_list_intensity)

    ms2_lib.close_ms2_file(ms2_file)


if __name__ == "__main__":
    main()
