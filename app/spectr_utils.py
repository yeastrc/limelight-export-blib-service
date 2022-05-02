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
from xml.dom import minidom
from . import __spectr_get_scan_data_env_key__


def generate_xml_for_post_request(scan_file_hash_key, scan_numbers):
    """Generate the XML to send to spectr to get the scan data for the scan numbers

    Parameters:
        scan_file_hash_key (string): The spectral file hash key for the spectral file
        scan_numbers (Array): The scan numbers in the file we want to get

    Returns:
        A string containing the generated XML
    """
    root = minidom.Document()

    root_elem = root.createElement('get_ScanDataFromScanNumbers_Request')
    root_elem.setAttribute('scanFileAPIKey', scan_file_hash_key)
    root_elem.setAttribute('includeParentScans', 'no')
    root.appendChild(root_elem)

    scan_numbers_elem = root.createElement('scanNumbers')
    root_elem.appendChild(scan_numbers_elem)

    for scan_number in scan_numbers:
        scan_number_elem = root.createElement('scanNumber')
        scan_numbers_elem.appendChild(scan_number_elem)

        scan_number_text = root.createTextNode(str(scan_number))
        scan_number_elem.appendChild(scan_number_text)

    return root.toxml()


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
    xml_for_post = generate_xml_for_post_request(scan_file_hash_key, scan_numbers)
    print('xml sent to spectr', xml_for_post)

    # send the post request
    headers = {'Content-Type': 'application/xml'}
    response = requests.post(spectr_url, data=xml_for_post, headers=headers)

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
        <get_ScanDataFromScanNumbers_Response>
            <status_scanFileAPIKeyNotFound>NO</status_scanFileAPIKeyNotFound>
            <scans>
                <scan level="2" scanNumber="27906" retentionTime="3565.1611" totalIonCurrentForScan="2876559.0"
                ionInjectionTime="74.98243" isCentroid="1" parentScanNumber="27905" precursorCharge="2"
                precursorMOverZ="414.74452368808">
                    <peaks>
                        <peak mz="899.999484" intensity="19999338.33" />
                        <peak mz="903.399883" intensity="88373.31" />
                        <peak mz="1003.87368" intensity="7733.84" />
                    </peaks>
                </scan>
                ... repeat for more <scan/> elements
            </scans>
        </uploadScanFile_Submit_Response>

    Parameters:
        response (requests.Response): The requests.Response from the spectr get data query
        scan_file_hash_key (string): The spectral file hash key for the spectral file

    Returns:
        An array of MS2ScanData objects, one for each scan
    """

    ms2_scan_data_objects = []

    dom = minidom.parseString(response.content)

    scan_elements = dom.getElementsByTagName('scan')

    if scan_elements is None or len(scan_elements) < 1:
        raise ValueError('Got spectr success, but found no scan elements in response', response.content)

    # parse each scan element, add it to the list of MS2ScanData objects we're returning
    for scan_element in scan_elements:
        msn_level = int(scan_element.getAttribute('level'))
        scan_number = int(scan_element.getAttribute('scanNumber'))
        retention_time_seconds = float(scan_element.getAttribute('retentionTime'))
        precursor_charge = int(scan_element.getAttribute('precursorCharge'))
        precursor_mz = float(scan_element.getAttribute('precursorMOverZ'))
        peak_list_intensity = []
        peak_list_mz = []

        peak_elements = scan_element.getElementsByTagName('peak')

        if peak_elements is None or len(peak_elements) < 1:
            raise ValueError('Found no peaks in scan ' + str(scan_number) + ' for spectr file ' + scan_file_hash_key)

        for peak_element in peak_elements:
            peak_list_intensity.append(float(peak_element.getAttribute('intensity')))
            peak_list_mz.append(float(peak_element.getAttribute('mz')))

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
