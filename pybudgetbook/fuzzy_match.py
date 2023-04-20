"""Tools for fuzzy group matching"""
import numpy as np
from difflib import get_close_matches


def match_group(data, reference_groups, use_fuzzy=False):
    # TODO Add brute force remark in doc
    # data is a row from DF this is used in apply

    # Loop groups and (fuzzy) match and count matche
    result = list()
    for key, grp in reference_groups.items():
        if use_fuzzy:
            matches = len(get_close_matches(data['Name'].casefold(), grp, cutoff=0.3, n=7))
        else:
            matches = sum([tester.casefold() in data['Name'].casefold() for tester in grp])
        if matches > 0:
            result.append((key, matches))

    # Best match
    if not result:
        return 'none'
    else:
        return result[np.array([match[1] for match in result]).argmax()][0]


def matcher_feedback(inp_data):
    """
    Feedback the data new to the matcher dict. This is pretty much brute force
    and there will be a certain overlap in basic and user data since matching
    works more generous than feedback. Anything else would be too complicated
    and since the data is fairly small its better to have more!
    """
    ...
