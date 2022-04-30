"""Methods for performing web-service functions for the web service"""

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


def _generate_json_for_status_request(request_id, status_text, message_text=None):
    """Generate the JSON to return for request status of blib conversion

    Generated JSON in the form of:
    {
      'request_id': <request id>,
      'status': <status string>,
      'error_message': <optional, error message if status is error>
      'blib_file_name': <optional, the file name of the created blib file if success>
    }

    Parameters:
        request_id (string): The unique key for the request
        status_text (string): The status text (e.g. 'success', 'error', 'queued', 'not found')
        message_text (string): The path to the blib file (if success), error message if error, otherwise None

    Returns:
        A string containing the generated JSON
    """

    response_json = {'request_id': request_id, 'status': status_text}

    if status_text == 'error' and message_text is not None:
        response_json['error_message'] = message_text

    elif status_text == 'success' and message_text is not None:
        response_json['blib_file_name'] = message_text

    return response_json


def get_json_for_status_request(status_request_data, request_status_dict):
    """Return the JSON to respond to a status request

    Parameters:
        status_request_data (dict): A string containing the request as json
        request_status_dict (dict): A dict containing status information

    Returns:
        string: A string containing the generated JSON
    """

    request_id = status_request_data['request_id']
    project_id = status_request_data['project_id']

    if request_id not in request_status_dict:
        return _generate_json_for_status_request(request_id, 'not found')

    if project_id != request_status_dict[request_id]['project_id']:
        return _generate_json_for_status_request(request_id, 'error', 'Project id does not match.')

    return _generate_json_for_status_request(
        request_id,
        request_status_dict[request_id]['status'],
        request_status_dict[request_id]['message']
    )


def cancel_conversion_request(cancel_request_data, request_queue, request_status_dict):
    """Remove the supplied request_id from the request_queue and request_status_dict

    Parameters:
        cancel_request_data (dict): The cancel request: {'request_id': request_id, 'project_id': project_id}
        request_queue (Array): The request queue, an array of dicts: {'id': request_id, 'data': xml_request}
        request_status_dict (dict): The dict that stores the status of requests

    Returns:
        dict: A simple dict in the form of {'cancel_message': <cancel message>}
    """

    request_id = cancel_request_data['request_id']
    project_id = cancel_request_data['project_id']

    if request_id not in request_status_dict:
        return {'cancel_message': 'Request id not found.'}

    if project_id != request_status_dict[request_id]['project_id']:
        return {'cancel_message': 'Project id does not match.'}

    # get index of request to remove
    idx = 0
    found = False
    for request in request_queue:
        if request['id'] == request_id:
            found = True
            break

        idx += 1

    if not found:
        return {'cancel_message': 'Request id not found.'}
    else:
        request_queue.pop(idx)

    del request_status_dict[request_id]

    return {'cancel_message': 'Removed.'}
