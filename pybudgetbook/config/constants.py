"""Containts package wide constants"""
import re
from pathlib import Path

"""
ALL CAPS consider constants which are most likely fixed and will stay in this
location. Small caps are constants which might get changed and even moved to
a better location in the future
"""
_MODULE_ROOT = Path(__file__).parent.parent
_FOLDER_STRUCT = {'data': None,
                  'backup': None,
                  'export': None,
                  }

_TARGET_DPI = 600
_TESS_OPTIONS = r'--psm 6'
_MANDATORY_COLS = ('Date', 'Vendor', 'ArtNr', 'Name', 'Units', 'PricePerUnit',
                   'Price', 'TaxClass', 'Group', 'Category')

_CATEGORIES = ['Supermarket', 'Cars & Gas', 'Clothing', 'Electronics', 'Other']

# Maps pattern with lang to set of regexp, general is alwazs used and the
# rest is updated on top!  -> constants so its closed
_patterns = {
    'gen_deu': {'simple_price_pattern': re.compile(r'(\d{1,3},\d{2})'),
                'price_with_class': re.compile(r'(\d{1,3},\d{2,3}_[AB12]|AW)'),
                'mult_pattern': re.compile(r'((?<=[xX*]_)\d{1,3},\d{2})'),
                'weight_pattern': re.compile(r'(\d{1,3},\d{1,3}(?=_EUR\/kg))'),
                'valid_article_pattern': re.compile(r'(.*?(?=(\d{1,3},\d{2})))'),
                'amount_in_weight': re.compile(r'(\b\d{1,2},\d{1,3})'),
                'total_sum_pattern': re.compile(
                    r'((?<=total_eur.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=betrag_eur.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=summe_eur.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=total.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=betrag.)\d{1,3}_*?,_*?\d{2})|'
                    r'((?<=summe.)\d{1,3}_*?,_*?\d{2})',
                    re.IGNORECASE)
                },
    'dm_deu': {'mult_pattern': re.compile(r'(\d{1,4}_*?(?=[xX*]))|((?<=[xX*])_*?\d{1,2},\d{1,3})'),
               'valid_article_pattern_mult': re.compile(
                   r'(?=_[a-zA-Z]).*?(?=_\d{1,2},\d{1,3})'),
               'negative_price': re.compile(r'-\d{1,3},\d{1,2}'),
               'total_sum_pattern': re.compile(
                   r'((?<=\bsumme_eur.)\d{1,3}_*?,_*?\d{2})',
                   re.IGNORECASE)
               },
    'unverpackt_deu': {
        'article_number': re.compile(r'\d{1,}'),
        'mult_pattern': re.compile(r'\d{1,2},\d{1,3}'),
        'total_sum_pattern': re.compile(r'((?<=summe.)\d{1,3}_*?,_*?\d{2})', re.IGNORECASE),
    },
}
