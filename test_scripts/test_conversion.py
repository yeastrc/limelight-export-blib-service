"""Script to test entire conversion process"""

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
import requests
import json
import time
from dotenv import load_dotenv

# load values from .env into env
load_dotenv()

service_host = 'localhost'
service_port = os.getenv('WEBAPP_PORT')

test_json_str = os.getenv('CONVERSION_TEST_JSON')
test_json_parsed = json.loads(test_json_str)

test_project_id = int(os.getenv('TEST_PROJECT_ID'))

# create request
url = 'http://' + service_host + ':' + service_port + '/requestNewBlibConversion'
print('Sending request to:', url, flush=True)
response = requests.post(url, json=test_json_parsed)
request_id = json.loads(response.text)['request_id']

print('Got request_id:', request_id, flush=True)

url = 'http://' + service_host + ':' + service_port + '/requestConversionStatus'
request_dict = {'project_id': test_project_id, 'request_id': request_id}

while True:
    response = requests.post(url, json=request_dict)
    print('Got status:', str(json.loads(response.text)), flush=True)

    time.sleep(10)
