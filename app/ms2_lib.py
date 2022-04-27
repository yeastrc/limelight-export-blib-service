"""Methods for writing .ms2 files"""

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

from . import __version__
from . import mass_utils
from datetime import datetime
import os


def write_scan_to_ms2_file(ms2_file, scan_number, precursor_mz, charge, peak_list_mz, peak_list_intensity):
    """Write the supplied scan data to the ms2_file

    Example scan lines:
        S	10	10	636.34
        Z	2	1271.67
        187.4 12.5
        193.1 19.5
        194.3 13.7
        198.3 29.8
        199.1 12.2

    Parameters:
        ms2_file (filehandle): ms2 file we are writing to
        scan_number (int): Scan number of the scan
        precursor_mz (float): Precursor m/z
        charge (int): Charge for this scan
        peak_list_mz (Array): array of m/z values from scan
        peak_list_intensity (Array): array of intensities corresponding to m/z array

    Returns:
        null
    """

    neutral_mass = mass_utils.get_neutral_mass_from_mz_and_charge(precursor_mz, charge)

    ms2_file.write("S\t" + str(scan_number) + "\t" + str(scan_number) + "\t" + str(precursor_mz) + "\n")
    ms2_file.write("Z\t" + str(charge) + "\t" + str(neutral_mass) + "\n")

    for mz, intensity in zip(peak_list_mz, peak_list_intensity):
        ms2_file.write(str(mz) + " " + str(intensity) + "\n")


def close_ms2_file(ms2_file):
    """Close the filehandle associated with this ms2 file

    Returns:
        null
    """
    ms2_file.close()


def initialize_ms2_file(path_to_directory, filename):
    """Create a file at path_to_directory, filename and write header (H) lines
    to it.

    Returns:
        File handle to the created file for subsequent writes of scan data
    """
    ms2_file = open(os.path.join(path_to_directory, filename), 'w')

    write_header_to_ms2_file(ms2_file, 'CreationDate', datetime.now().strftime("%Y%m%d"))
    write_header_to_ms2_file(ms2_file, 'Extractor', 'Limelight blib exporter, Spectr to MS2')
    write_header_to_ms2_file(ms2_file, 'ExtractorVersion', __version__)
    write_header_to_ms2_file(ms2_file, 'Comments', 'See: https://github.com/yeastrc/limelight-export-blib-service')

    return ms2_file


def write_header_to_ms2_file(ms2_file, header_key, header_value):
    """Append the supplied key/value pair as a header to the supplied file
    handle

    Example header lines:

        H	CreationDate	20200323
        H	Extractor	Limelight Spectr to MS2
        H	ExtractorVersion	1.0
        H	Comments	MakeMS2 written by Michael J. MacCoss, 2004
        H	ExtractorOptions	MS2/MS1

    Returns:
        null
    """
    ms2_file.write("H\t" + header_key + "\t" + header_value + "\n")
