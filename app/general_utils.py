import uuid


def generate_request_id():
    return str(uuid.uuid4())


def build_peptide_string_with_mods(peptide_sequence, mods):
    """Build a peptide string from a sequence and set of modifications. E.g., "PEPTIDE" and
    mods of {'3':28.32} becomes "PEP[28.32]TIDE"

    Parameters:
        peptide_sequence (string): The naked peptide sequence (no mods)
        mods (dict): { position_value: x }

    Returns:
        string: the formatted peptide string
    """

    if mods is None or len(mods) < 1:
        return peptide_sequence

    # handle terminal mods
    if 'n' in mods:
        if '1' in mods:
            mods['1'] = mods['1'] + mods['n']
        else:
            mods['1'] = mods['n']

        del mods['n']

    if 'c' in mods:
        pep_len = str(len(peptide_sequence))

        if pep_len in mods:
            mods[pep_len] = mods[pep_len] + mods['c']
        else:
            mods[pep_len] = mods['c']

        del mods['c']

    # we are ignoring unlocalized mods for now
    # handle unlocalized mods--just set them as n-terminal mods
    # if 'u' in mods:
    #     if '1' in mods:
    #         mods['1'] = mods['1'] + mods['u']
    #     else:
    #         mods['1'] = mods['u']
    #
    #     del mods['u']

    output_string = ''

    for element in range(0, len(peptide_sequence)):

        output_string += peptide_sequence[element]

        if str(element + 1) in mods:
            mass = mods[str(element + 1)]
            mass_str = str(mass)
            if mass > 0:
                mass_str = '+' + mass_str

            output_string += '[' + mass_str + ']'

    return output_string
