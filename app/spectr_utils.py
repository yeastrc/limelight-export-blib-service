"""Methods for interacting with spectr spectra web services"""

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
from . import __spectr_get_scan_data_env_key__


def generate_ob_for_post_request(scan_file_hash_key, scan_numbers):
    """Generate the JSON to send to spectr to get the scan data for the scan numbers

    Parameters:
        scan_file_hash_key (string): The spectral file hash key for the spectral file
        scan_numbers (Array): The scan numbers in the file we want to get

    Returns:
        dict: A dict to send to spectr as JSON
    """

    ob = {'scanFileAPIKey': scan_file_hash_key, 'includeParentScans': 'NO', 'scanNumbers': scan_numbers}

    return ob


def get_scan_data_for_scan_numbers(scan_file_hash_key, scan_numbers):
    """Get scan data from spectr for the given scan numbers and file hash

    Parameters:
        scan_file_hash_key (string): The spectral file hash key for the spectral file
        scan_numbers (Array): The scan numbers in the file we want to get

    Returns:
        An array of MS2ScanData objects, one for each scan
    """

    # request the scan data from spectr
    spectr_url = os.environ.get(__spectr_get_scan_data_env_key__)
    if spectr_url is None:
        raise ValueError('No ' + __spectr_get_scan_data_env_key__ + ' env variable is set.')

    # the xml we're sending in the post request
    ob_for_post = generate_ob_for_post_request(scan_file_hash_key, scan_numbers)

    # send the post request
    headers = {'Content-Type': 'application/json'}
    response = requests.post(spectr_url, json=ob_for_post, headers=headers)

    return parse_spectr_response(response, scan_file_hash_key)


def parse_spectr_response(response, scan_file_hash_key):
    """Parse the requests.Response from the spectr get data query

    Parameters:
        response (requests.Response): The requests.Response from the spectr get data query
        scan_file_hash_key (string): The spectral file hash key for the spectral file

    Returns:
        An array of MS2ScanData objects, one for each scan
    """

    # whoopsie, we got an error.
    if response.status_code != 200:
        return handle_spectr_error(response, scan_file_hash_key)

    return handle_spectr_success(response, scan_file_hash_key)


def handle_spectr_success(response, scan_file_hash_key):
    """Handle a response that is a spectr success

    example of successful response:
        {
            "status_scanFileAPIKeyNotFound":null,
            "scans":[
                {
                    "level":1,
                    "scanNumber":2,
                    "retentionTime":0.4104105,
                    "totalIonCurrent_ForScan":1.6223904E7,
                    "ionInjectionTime":50.0,
                    "isCentroid":1,
                    "parentScanNumber":null,
                    "precursorCharge":null,
                    "precursor_M_Over_Z":null,
                    "peaks":[
                        {
                            "mz":400.2538146972656,
                            "intensity":5292.239
                        },
                    ]
                },
            ]
        }

    Parameters:
        response (requests.Response): The requests.Response from the spectr get data query
        scan_file_hash_key (string): The spectral file hash key for the spectral file

    Returns:
        An array of MS2ScanData objects, one for each scan
    """

    ms2_scan_data_objects = []

    response_ob = json.loads(response.text)

    if 'scans' not in response_ob:
        raise ValueError('Got spectr success, but found no scan elements in response', response.content)

    scans = response_ob['scans']

    if len(scans) < 1:
        raise ValueError('Got spectr success, but found no scan elements in response', response.content)

    # parse each scan element, add it to the list of MS2ScanData objects we're returning
    for scan_ob in scans:
        msn_level = scan_ob['level']
        scan_number = scan_ob['scanNumber']
        retention_time_seconds = scan_ob['retentionTime']
        precursor_charge = scan_ob['precursorCharge']
        precursor_mz = scan_ob['precursor_M_Over_Z']
        peak_list_intensity = []
        peak_list_mz = []

        peaks = scan_ob['peaks']

        if peaks is None or len(peaks) < 1:
            raise ValueError('Found no peaks in scan ' + str(scan_number) + ' for spectr file ' + scan_file_hash_key)

        for peak_ob in peaks:
            peak_list_intensity.append(peak_ob['intensity'])
            peak_list_mz.append(peak_ob['mz'])

        ms2_scan_data = MS2ScanData(
            scan_file_hash_key=scan_file_hash_key,
            scan_number=scan_number,
            msn_level=msn_level,
            precursor_charge=precursor_charge,
            precursor_mz=precursor_mz,
            retention_time_seconds=retention_time_seconds,
            peak_list_intensity=peak_list_intensity,
            peak_list_mz=peak_list_mz
        )

        ms2_scan_data_objects.append(ms2_scan_data)

    return ms2_scan_data_objects


def handle_spectr_error(response, scan_file_hash_key):
    """Handle a response that is a spectr error

    Parameters:
        response (requests.Response): The requests.Response from the spectr get data query
        scan_file_hash_key (string): The spectral file hash key for the spectral file

    Returns:
        None, will always raise an exception
    """

    if str(response.status_code).startswith('5'):
        raise ValueError('Got ' + str(response.status_code) + ' error. May be an invalid spectr file id.')

    if str(response.status_code).startswith('4'):
        raise ValueError('Got ' + str(response.status_code) + ' error. Double check spectr URL.')

    if str(response.status_code).startswith('3'):
        raise ValueError('Got ' + str(response.status_code) + ' error. Has a redirect been set up. Use final URL.')

    # error caused by unknown reason. return error code and reported reason
    error_text = 'Spectr: Got error code: ' + str(response.status_code) + ': ' + response.reason
    raise ValueError(error_text)


class MS2ScanData:
    def __init__(self,
                 scan_file_hash_key,
                 scan_number,
                 msn_level,
                 retention_time_seconds,
                 precursor_charge,
                 precursor_mz,
                 peak_list_intensity,
                 peak_list_mz):
        """Create a MS2ScanData object

        Parameters:
            scan_file_hash_key (string): The spectral file hash key for the spectral file
            scan_number (int): Scan number for this scan
            retention_time_seconds (float): Retention time of this scan in seconds
            precursor_charge (int): Estimated charge of precursor ion
            precursor_mz (float): Measured m/z of precursor ion
            peak_list_intensity (Array): An array of peak list intensities
            peak_list_mz (Array): An array of peak list mz values

        Returns:
            Populated MS2ScanData object
        """
        self._scan_file_hash_key = scan_file_hash_key
        self._scan_number = scan_number
        self._msn_level = msn_level
        self._precursor_charge = precursor_charge
        self._precursor_mz = precursor_mz
        self._retention_time_seconds = retention_time_seconds
        self._peak_list_intensity = peak_list_intensity
        self._peak_list_mz = peak_list_mz

    @property
    def scan_file_hash_key(self):
        return self._scan_file_hash_key

    @scan_file_hash_key.setter
    def scan_file_hash_key(self, value):
        self._scan_file_hash_key = value

    @property
    def scan_number(self):
        return self._scan_number

    @scan_number.setter
    def scan_number(self, value):
        self._scan_number = value

    @property
    def precursor_charge(self):
        return self._precursor_charge

    @precursor_charge.setter
    def precursor_charge(self, value):
        self._precursor_charge = value

    @property
    def precursor_mz(self):
        return self._precursor_mz

    @precursor_mz.setter
    def precursor_mz(self, value):
        self._precursor_mz = value

    @property
    def msn_level(self):
        return self._msn_level

    @msn_level.setter
    def msn_level(self, value):
        self._msn_level = value

    @property
    def retention_time_seconds(self):
        return self._retention_time_seconds

    @retention_time_seconds.setter
    def retention_time_seconds(self, value):
        self._retention_time_seconds = value

    @property
    def peak_list_intensity(self):
        return self._peak_list_intensity

    @peak_list_intensity.setter
    def peak_list_intensity(self, value):
        self._peak_list_intensity = value

    @property
    def peak_list_mz(self):
        return self._peak_list_mz

    @peak_list_mz.setter
    def peak_list_mz(self, value):
        self._peak_list_mz = value
