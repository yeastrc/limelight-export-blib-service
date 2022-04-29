"""Start up the service"""

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
from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
import threading
from app import general_utils, web_service_utils, request_handler, request_status_dict, request_queue, \
    request_queue_status, __webapp_port_env_key__

app = Flask(__name__)
api = Api(app)


class RequestConversionStatus(Resource):
    """Web service for retrieving conversion status"""

    def post(self):
        json_data = request.get_json(force=True)

        if 'request_id' not in json_data or 'project_id' not in json_data:
            return 'Required data not present', 400

        return web_service_utils.get_json_for_status_request(json_data, request_status_dict), 200


class RequestBlibConversion(Resource):
    """Web service for requesting a blib conversion"""

    def post(self):
        json_data = request.get_json(force=True)

        if 'project_id' not in json_data or 'spectral_data' not in json_data:
            return 'Required data not present', 400

        request_id = general_utils.generate_request_id()
        project_id = json_data['project_id']
        spectral_data = json_data['spectral_data']

        print('Conversion request:')
        print('\tDate:', datetime.today().strftime('%Y-%m-%d'))
        print('\tproject_id:', project_id)
        print('\trequest_id:', request_id)

        request_queue.append({'id': request_id, 'data': spectral_data})
        request_status_dict[request_id] = {
            'project_id': project_id,
            'status': 'queued',
            'message': None
        }

        if not request_queue_status['started']:
            request_queue_status['started'] = True

            # start request processor in a separate thread
            thread = threading.Thread(
                target=request_handler.process_request_queue,
                args=(request_queue, request_status_dict)
            )
            thread.start()

        return request_id, 200


api.add_resource(RequestBlibConversion, '/requestNewBlibConversion')
api.add_resource(RequestConversionStatus, '/requestConversionStatus')

if __name__ == '__main__':

    port = os.getenv(__webapp_port_env_key__)
    if port is None:
        raise ValueError('No port is defined by env. var.: ' + __webapp_port_env_key__)
    app.run(debug=True, port=int(port))
