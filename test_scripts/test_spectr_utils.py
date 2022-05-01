"""Simple script to test functionality of app/spectr_utils"""

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
from app import __spectr_get_scan_data_env_key__, spectr_utils
from dotenv import load_dotenv

# load values from .env into env
load_dotenv()

spectr_get_url = os.getenv('SPECTR_GET_SCAN_DATA_URL')
scan_number_list = os.getenv('TEST_SCAN_NUMBERS').strip('][').split(', ')
spectr_file_id = os.getenv('TEST_SPECTR_FILE_ID')


def main():

    # set the env var needed to get data from spectr
    os.environ[__spectr_get_scan_data_env_key__] = spectr_get_url

    # do the work
    results = spectr_utils.get_scan_data_for_scan_numbers(spectr_file_id, scan_number_list)

    # print results:
    print('Number of results: ', len(results))

    for result in results:
        print('\tScan number: ', result.scan_number)
        print('\tMSn level: ', result.msn_level)
        print('\tRT (s): ', result.retention_time_seconds)
        print('\tPeak m/zs', result.peak_list_mz)
        print('\tPeak intensities', result.peak_list_intensity)
        print('\n')


if __name__ == "__main__":
    main()
