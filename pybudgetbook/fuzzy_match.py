"""Tools for fuzzy group matching"""
import logging
import numpy as np
import re
from difflib import get_close_matches

# TODO relative
import pybudgetbook.config.config as bbconfig
from pybudgetbook import bb_io


logger = logging.getLogger(__package__)


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


def matcher_feedback(retrieved_data):
    """
    Feedback the data new to the matcher dict. This is pretty much brute force
    and there will be a certain overlap in basic and user data since matching
    works more generous than feedback. Anything else would be too complicated
    and since the data is fairly small its better to have more!
    """
    user_match_data, user_match_file = bb_io.load_user_match_data(bbconfig.options['lang'])
    basic_match_data, _ = bb_io.load_basic_match_data(bbconfig.options['lang'])
    neg_match_data = bb_io.load_negative_match_data(bbconfig.options['lang'])

    remove_trash = re.compile(r'[^a-z0-9 äöü]', re.IGNORECASE)
    remove_weight = re.compile(r'\d{1,4}_*?[km]*?[gl]', re.IGNORECASE)

    for feedname, feedgroup in zip(retrieved_data['Name'], retrieved_data['Group']):
        if feedgroup in basic_match_data:
            if feedname in basic_match_data[feedgroup]:
                logger.debug('This article is already matched in the basic data set')
                continue

        if feedgroup not in user_match_data:
            if feedgroup == 'none': continue
            error = (f'Group {feedgroup:s} does not exist in user group data '
                     'and creating is not enabled, check for '
                     'typos and / enable flag!')
            logger.error(error)
            raise RuntimeError(error)

        feedback = [substring.casefold() for substring in
                    remove_weight.sub('', remove_trash.sub('', feedname)).split(' ')
                    if substring and len(substring) > 2]

        # Fuzzy backcheck to reduce redundancy...
        if feedgroup in basic_match_data:
            fuzzy_fb_vs_bsic = [not bool(get_close_matches(fb, basic_match_data[feedgroup]))
                                for fb in feedback]
            feedback = list(np.array(feedback)[fuzzy_fb_vs_bsic])

        # ...and negative tagged
        if feedback:
            fuzzy_fb_vs_neg = [not bool(get_close_matches(fb, neg_match_data))
                               for fb in feedback]
            feedback = list(np.array(feedback)[fuzzy_fb_vs_neg])

        user_match_data[feedgroup] = list(set(user_match_data[feedgroup]).union(
            set(feedback)))

    bb_io._save_user_match_data(user_match_data, user_match_file)
