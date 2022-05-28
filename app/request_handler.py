"""Handle processing of the request queue"""

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
import time
import shutil
import subprocess
import traceback
from mpire import WorkerPool
from . import __request_check_delay__, __workdir_env_key__, __blib_dir_env_key__, __spectr_batch_size_env_key__, \
    __blib_build_executable_path_env_key__, __blib_filter_executable_path_env_key__,\
    __clean_working_directory_env_key__, __ms2_max_threads_env_key__, ssl_lib, ms2_lib, general_utils, spectr_utils


def process_request_queue(request_queue, request_status_dict):
    """Serially process all requests in the request queue

    Parameters:
        request_queue (list): The request queue, a list of dicts: {'id': request_id, 'data': xml_request}
        request_status_dict (dict): The dict that stores the status of requests

    Returns:
        None
    """

    while True:
        while len(request_queue) > 0:
            request = request_queue.pop(0)

            process_request(request, request_status_dict)

        time.sleep(__request_check_delay__)


def process_request(request, request_status_dict):
    """Process the given request. Should not ever raise an exception. Will update the
    request status dict appropriately.

    Parameters:
        request (dict): A dict: {'id': request_id, 'data': xml_request}
        request_status_dict (dict): The dict that stores the status of requests

    Returns:
        None
    """

    workdir = None

    try:

        request_status_dict[request['id']]['status'] = 'processing'
        request_status_dict[request['id']]['end_user_message'] = 'Exporting SSL and gathering scans.'

        final_blib_filename = request['id'] + '.blib'
        verify_blib_destination(final_blib_filename)
        workdir = get_workdir(request)

        ssl_file_name = 'export.ssl'
        ssl_file = ssl_lib.initialize_ssl_file(workdir, ssl_file_name)

        request_data = request['data']

        percent_per_file = 100 / len(request_data)
        percent_done = 0
        request_status_dict[request['id']]['end_user_message'] = 'Exporting scan files: 0% complete...'

        # hold the data returned from processing each ms2
        result_dicts = {}

        max_threads = get_ms2_max_threads()

        # create each ms2 file using a multiprocessing workerpool
        if max_threads > 1:
            with WorkerPool(n_jobs=max_threads, pass_worker_id=False) as pool:
                for result_dict in pool.imap_unordered(create_ms2_file, zip(request_data, range(1, len(request_data) + 1), [workdir] * len(request_data)), iterable_len=len(request_data), progress_bar=False):
                    percent_done += percent_per_file
                    request_status_dict[request['id']]['end_user_message'] = 'Exporting scan files: ' +\
                                                                             str(round(percent_done, 1)) +\
                                                                             '% complete...'

                    result_dicts[result_dict['spectr_file_id']] = result_dict
        else:
            counter = 1
            for spectr_dict in request_data:
                request_status_dict[request['id']]['end_user_message'] = 'Exporting scan files: ' + \
                                                                         str(round(percent_done, 1)) + \
                                                                         '% complete...'
                result_dict = create_ms2_file(spectr_dict, counter, workdir)
                result_dicts[result_dict['spectr_file_id']] = result_dict

                percent_done += percent_per_file
                counter += 1

        for spectr_dict in request_data:
            spectr_file_id = spectr_dict['spectr_file_id']
            ms2_file_name = result_dicts[spectr_file_id]['ms2_file_name']
            retention_time_dict = result_dicts[spectr_file_id]['retention_times']

            # write out lines to ssl file
            for psm in spectr_dict['psms']:
                scan_number = psm['scan_number']
                charge = psm['charge']
                retention_time_minutes = retention_time_dict[scan_number] / 60

                if 'modifications' not in psm:
                    psm['modifications'] = {}

                peptide_sequence = general_utils.build_peptide_string_with_mods(
                    psm['peptide_sequence'],
                    psm['modifications']
                )

                ssl_lib.write_psm_to_ssl_file(
                    ssl_file,
                    ms2_file_name,
                    scan_number,
                    charge,
                    peptide_sequence,
                    retention_time_minutes
                )

            # done iterating over PSMs in this scan file

        # done iterating over scan files
        ssl_lib.close_ssl_file(ssl_file)

        # create redundant blib
        request_status_dict[request['id']]['end_user_message'] = 'Generating redundant blib file'
        redundant_blib_filename = request['id'] + '.redundant.blib'
        execute_blib_build_conversion(
            redundant_blib_filename,
            ssl_file_name,
            workdir
        )

        # filter redundant blib into final blib
        request_status_dict[request['id']]['end_user_message'] = 'Generating filtered blib file'
        execute_blib_filter(
            redundant_blib_filename,
            final_blib_filename,
            workdir
        )

        # move to final location
        request_status_dict[request['id']]['end_user_message'] = 'Moving .blib to final location'
        blib_destination_path = os.getenv(__blib_dir_env_key__)
        move_blib_to_final_destination(
            workdir,
            request_status_dict[request['id']]['project_id'],
            final_blib_filename
        )

        request_status_dict[request['id']]['status'] = 'success'
        request_status_dict[request['id']]['message'] = request['id'] + '.blib'

        clean_workdir(workdir, success=True)

    except Exception as e:
        request_status_dict[request['id']]['status'] = 'error'
        request_status_dict[request['id']]['message'] = str(e)

        # print stack trace
        traceback.print_exc()

        clean_workdir(workdir, success=False)


def get_ms2_max_threads():
    """Get the number of threads to use to build ms2 files. Defaults to 1 if no env var is set

    Returns:
        int: the number of threads to use
    """

    max_threads = os.getenv(__ms2_max_threads_env_key__)

    if max_threads is None:
        max_threads = 1
    else:
        max_threads = int(max_threads)

    return max_threads


def get_distinct_scans_from_request_data(request_data_spectr_chunk):
    """Get sorted list of all distinct scan numbers in the given spectr chunk of the request data

    Parameters:
        request_data_spectr_chunk (dict): A dict containing the conversion request for one scan file

    Returns:
        list: The distinct scan numbers, no order is implied
    """

    distinct_scans = set()

    # write out lines to ssl file, capture scan numbers to include in .ms2
    for psm in request_data_spectr_chunk['psms']:
        scan_number = psm['scan_number']

        distinct_scans.add(scan_number)

    ret_list = list(distinct_scans)
    ret_list.sort()

    return ret_list


def execute_blib_filter(redundant_blib_filename, final_blib_filename, workdir):
    """Run BlibFilter on the supplied redundant_blib_filename to produce final_blib_filename

    Parameters:
        redundant_blib_filename (string): The filename of the redundant blib produced by BlibBuild
        final_blib_filename (string): The filename to be produced by running BlibFilter
        workdir (string): Full path to where the .redundant.blib and .blib files are located

    Returns:
        NoneType
    """

    blib_filter_executable = os.getenv(__blib_filter_executable_path_env_key__)
    if not os.path.exists(blib_filter_executable):
        raise ValueError('Could not find BlibFilter executable:', blib_filter_executable)

    if not blib_filter_executable.endswith('BlibFilter'):
        raise ValueError('Blib filter executable must have the name BlibFilter.')

    result = subprocess.run(
        [blib_filter_executable, redundant_blib_filename, final_blib_filename],
        cwd=workdir,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    verify_file_exists(os.path.join(workdir, final_blib_filename))

    if result.returncode != 0:
        raise ValueError("Non-zero return code from BlibFilter. Error message:", result.stderr)


def execute_blib_build_conversion(library_name, ssl_file_name, workdir):
    """Convert the given ssl file to a .blib spectral library

    Parameters:
        library_name (string): The base file name of the .blib file (do not include .blib)
        ssl_file_name (string): The filename of the .ssl file we are processing
        workdir (string): Full path to where the .ssl and .ms2 files are located

    Returns:
        NoneType
    """

    blib_executable = os.getenv(__blib_build_executable_path_env_key__)
    if not os.path.exists(blib_executable):
        raise ValueError('Could not find BlibOut executable:', blib_executable)

    if not blib_executable.endswith('BlibBuild'):
        raise ValueError('Blib executable must have the name BlibBuild.')

    result = subprocess.run(
        [blib_executable, '-H', '-K', ssl_file_name, library_name],
        cwd=workdir,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    verify_file_exists(os.path.join(workdir, library_name))

    if result.returncode != 0:
        raise ValueError("Non-zero return code from BlibBuild. Error message:", result.stderr)


def move_blib_to_final_destination(workdir, project_id, blib_file_name):
    """Move the blib file to its final location, will remove it from the original location

    Parameters:
        workdir (string): Full path to the working directory
        project_id (int): The limelight project id
        blib_file_name (string): The filename of the .blib file: 'something.blib'

    Returns:
        NoneType
    """
    if not os.path.exists(workdir):
        raise ValueError('Working directory does not exist:', workdir)

    if not os.path.exists(os.path.join(workdir, blib_file_name)):
        raise ValueError('Attempting to move blib that does not exist:', os.path.join(workdir, blib_file_name))

    if os.getenv(__blib_dir_env_key__) is None:
        raise ValueError('Blib destination dir env var not defined:', __blib_dir_env_key__)

    blib_destination_dir = os.getenv(__blib_dir_env_key__)
    if not os.path.exists(blib_destination_dir):
        raise ValueError('Blib destination dir does not exist:', blib_destination_dir)

    # place the resulting blib in the blib_destination_dir/project_id/
    blib_destination_dir = os.path.join(blib_destination_dir, str(project_id))
    if not os.path.exists(blib_destination_dir):
        os.mkdir(blib_destination_dir)

    # move the resulting .blib to the final location
    shutil.move(
        os.path.join(workdir, blib_file_name),
        os.path.join(blib_destination_dir, blib_file_name)
    )

    verify_file_exists(os.path.join(workdir, os.path.join(blib_destination_dir, blib_file_name)))


def verify_file_exists(file_path):
    """Verify the file at the given path exists, raise exception if not

    Parameters:
        file_path (string): Full path to blib file

    Returns:
        NoneType
    """

    if not os.path.exists(file_path):
        raise ValueError('Expected file not found:', file_path)


def create_ms2_file(spectr_dict, ms2_file_id, workdir):
    """Create a MS2 file from a spectr file id for the given scans

    Parameters:
        spectr_dict (dict): The part of the conversion request for a single spectr file id
        ms2_file_id (int): The base of the filename to use for the ms2 file (e.g., 1 = '1.ms2'
        workdir (string): Full path to the working directory

    Returns:
        dict: The retention times found for each scan in the form of:
            {
                'spectr_file_id': <spectr file id>,
                'ms2_file_name': <ms2 file name>,
                'retention_times': {
                    <scan number>: <retention time in s>,
                }
            },
    """

    spectr_file_id = spectr_dict['spectr_file_id']
    ms2_file_name = str(ms2_file_id) + '.ms2'
    scans_to_add = get_distinct_scans_from_request_data(spectr_dict)

    scan_count_per_call = os.getenv(__spectr_batch_size_env_key__)
    if scan_count_per_call is None:
        raise ValueError('Missing environmental variable:', __spectr_batch_size_env_key__)

    retention_time_dict = {}
    scan_count_per_call = int(scan_count_per_call)

    scan_sets = [scans_to_add[i:i + scan_count_per_call] for i in range(0, len(scans_to_add), scan_count_per_call)]

    ms2_file = ms2_lib.initialize_ms2_file(workdir, ms2_file_name)

    try:
        for scan_array in scan_sets:
            scan_data = spectr_utils.get_scan_data_for_scan_numbers(spectr_file_id, scan_array)

            for ms2_scan in scan_data:
                ms2_lib.write_scan_to_ms2_file(
                    ms2_file,
                    ms2_scan.scan_number,
                    ms2_scan.precursor_mz,
                    ms2_scan.precursor_charge,
                    ms2_scan.peak_list_mz,
                    ms2_scan.peak_list_intensity
                )
                retention_time_dict[ms2_scan.scan_number] = ms2_scan.retention_time_seconds

    finally:
        ms2_lib.close_ms2_file(ms2_file)

    return {
        'spectr_file_id': spectr_file_id,
        'ms2_file_name': ms2_file_name,
        'retention_times': retention_time_dict
    }


def clean_workdir(workdir, success):
    """Remove the supplied directory and all files within. Swallows all exceptions but prints out
    error message

    Parameters:
        workdir (string): Full path to the desired directory
        success (bool): Whether the request was completed successfully

    Returns:
        NoneType
    """

    if get_should_clean_workdir(success):
        if workdir is not None and os.path.exists(workdir):
            try:
                shutil.rmtree(workdir)
            except OSError as e:
                print('Error cleaning workdir: ', workdir)


def get_should_clean_workdir(success):
    """Determine whether the working directory should be deleted. Uses the environmental
    variable to determine behavior. If that variable is set to 'no', never delete. If
    set to 'yes', always delete. If set to 'on success', only delete on success. Defaults
    to 'yes' if that variable is not set.

    Parameters:
        success (bool): Whether the request was completed successfully

    Returns:
        bool
    """

    workdir_deletion_config_string = os.getenv(__clean_working_directory_env_key__)

    if workdir_deletion_config_string is None:
        workdir_deletion_config_string = 'yes'

    if workdir_deletion_config_string == 'no':
        return False

    if workdir_deletion_config_string == 'yes':
        return True

    if workdir_deletion_config_string == 'on success':
        return success

    raise ValueError('Got unknown value for env var:', __clean_working_directory_env_key__)


def verify_blib_destination(blib_filename):
    """Verify a blib output dir is defined and that it exists. Verify a destination file with our
    request id doesn't already exist. Will raise an Exception for any of these circumstances.

    Returns:
        NoneType
    """

    blib_dir = os.getenv(__blib_dir_env_key__)

    if blib_dir is None:
        raise ValueError('No blib destination variable defined:', __blib_dir_env_key__)

    if not os.path.exists(blib_dir):
        raise ValueError('Blib directory does not exist: ', os.getenv(__blib_dir_env_key__))

    destination_file = os.path.join(blib_dir, blib_filename)
    if os.path.exists(destination_file):
        raise ValueError('Blib destination file already exists:', destination_file)


def get_workdir(request):
    """Create and return the path to the work directory

    Parameters:
        request (dict): A dict: {'id': request_id, 'data': xml_request}

    Returns:
        string
    """

    if os.getenv(__workdir_env_key__) is None:
        raise ValueError('No environmental variable defined:', __workdir_env_key__)

    if not os.path.exists(os.getenv(__workdir_env_key__)):
        raise ValueError('Directory does not exist: ', os.getenv(__workdir_env_key__))

    if not os.path.isdir(os.getenv(__workdir_env_key__)):
        raise ValueError('Work directory is a file, not a directory:', os.getenv(__workdir_env_key__))

    workdir = os.path.join(os.getenv(__workdir_env_key__), request['id'])
    if os.path.exists(workdir):
        raise ValueError('Work directory already exists:', workdir)

    os.mkdir(workdir)
    if not os.path.exists(workdir):
        raise ValueError('Failed to create work directory:', workdir)

    return workdir
