"""Simple script to test functionality of app/ssl_lib"""

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
from app import ssl_lib
from dotenv import load_dotenv

# load values from .env into env
load_dotenv()

ssl_file_name = os.getenv('TEST_SSL_FILE_NAME')
ssl_file_directory = '.'

test_psm_peptides = ['VGAGAPVYLAAVLEYLAAEVLELAGNAAR', 'LAESITIEQGK', 'ELAEDGC[+57.0]SGVEVR']
test_psm_charges = [3, 3, 2]
test_psm_scan_numbers = [8, 1806, 2572]
test_ms2_file_name = 'test.ms2'


def main():

    ssl_file = ssl_lib.initialize_ssl_file(ssl_file_directory, ssl_file_name)

    for items in zip(test_psm_peptides, test_psm_charges, test_psm_scan_numbers):
        ssl_lib.write_psm_to_ssl_file(ssl_file, test_ms2_file_name, items[2], items[1], items[0])

    ssl_lib.close_ssl_file(ssl_file)


if __name__ == "__main__":
    main()
