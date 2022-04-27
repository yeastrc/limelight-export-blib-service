"""Methods for writing .ssl files for import into BlibBuild"""

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

import os.path


def write_psm_to_ssl_file(ssl_file, ms2_filename, scan_number, charge, sequence):
    """Create a psm entry to the ssl file. Example ssl file:

    file   scan    charge  sequence
    demo.ms2        8       3       VGAGAPVYLAAVLEYLAAEVLELAGNAAR
    demo.ms2        1806    2       LAESITIEQGK
    demo.ms2        2572    2       ELAEDGC[+57.0]SGVEVR
    demo.ms2        3088    2       TTAGAVEATSEITEGK
    demo.ms2        3266    2       DC[+57.0]EEVGADSNEGGEEEGEEC[+57.0]
    demo.ms2        9734    3       IWELEFPEEAADFQQQPVNAQ[-17.0]PQN
    demo.ms2        20919   3       VHINIVVIGHVDSGK
    ../elsewhere/spec.mzXML 00497   2       LKEPAQNTADNAK
    ../elsewhere/spec.mzXML 00680   2       ALEGPGPGEDAAHSENNPPR
    ../elsewhere/spec.mzXML 00965   2       FFSHEAEQK
    ../elsewhere/spec.mzXML 01114   2       C[+57.0]GPSQPLK
    ../elsewhere/spec.mzXML 01382   2       AVHVQVTDAEAGK

    Returns:
        None
    """

    ssl_file.write(ms2_filename + "\t" + str(scan_number) + "\t" + str(charge) + "\t" + str(sequence) + "\n")


def initialize_ssl_file(path_to_directory, filename):
    """Create a new .ssl file at path_to_directory

    Returns:
        File handle to the created file for subsequent writes of scan data
    """
    ssl_file = open(os.path.join(path_to_directory, filename), 'w')

    ssl_file.write("file\tscan\tcharge\tsequence\n")

    return ssl_file


def close_ssl_file(ssl_file):
    """Cleanly close the ssl file

    Returns:
        None
    """
    ssl_file.close()
