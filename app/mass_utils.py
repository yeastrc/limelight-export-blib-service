"""Methods for mass calculations"""

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

proton_mass = 1.007276466621


def get_neutral_mass_from_mz_and_charge(mz, charge):
    """Calculate and return the neutral mass given the mz and charge

    Parameters:
        mz: The m/z
        charge (int): The charge (z)

    Returns:
        float: The neutral mass
    """
    mass = mz * charge
    mass -= charge * proton_mass

    return mass
