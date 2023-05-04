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
_VIEWER_COLS = ('ArtNr', 'Name', 'Units', 'PricePerUnit', 'Price', 'TaxClass',
                'Group')

_CATEGORIES = ['Supermarket', 'Small Stores', 'Cars & Gas', 'Clothing', 'Electronics', 'Other']

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
                    re.IGNORECASE),
                'date_pattern': re.compile(
                    r'[0-3]\d[,.\/]_*?[0,1]\d[,.\/]_*?(2[0,1]\d{2}|\d{2})'),
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
    'real_deu': {},  # inherits all, but the flag is needed for sorting
    'tank_deu': {'price_with_class_2': re.compile(r'(\d{1,3},\d{2,3}(?=_*?[EUR]{0,3}-[AB12]))')
                 },
    'raiff_deu': {'price_with_class': re.compile(r'(\d{1,3}[,.]\d{2,3}_[AB12I\]\[]|AW)'),
                  'mult_pattern': re.compile(r'(\d{1,3}(?=[xX*]))'),
                  'mult_price': re.compile(r'((?<=[xX*])_*?\d{1,3}[.,]\d{1,2})'),
                  'valid_article_pattern': re.compile(r'(.*?(?=(\d{1,3}[,.]\d{2})))'),
                  'total_sum_pattern': re.compile(r'((?<=summe.))_*?\d{1,3}_*?[,.]_*?\d{2}', re.IGNORECASE),
            },
}

_icon_root = Path('pybudgetbook/img/groups')
icons = {
    'Grundnahrungsmittel': str(_icon_root / 'general.png'),
    'Milchprodukte': str(_icon_root / 'dairy.png'),
    'Gemüse': str(_icon_root / 'veggies.png'),
    'Früchte': str(_icon_root / 'fruit.png'),
    'Beeren': str(_icon_root / 'berry.png'),
    'Wurst / Käse': str(_icon_root / 'sausage.png'),
    'Süßes': str(_icon_root / 'sweets.png'),
    'Getränke': str(_icon_root / 'drinks.png'),
    'Alkohol': str(_icon_root / 'alco.png'),
    'Haushalt': str(_icon_root / 'house_gen.png'),
    'Drogerie': str(_icon_root / 'drugstore.png'),
    'Kinder': str(_icon_root / 'kids.png'),
    'Bäcker': str(_icon_root / 'bakery.png'),
    'Auto': str(_icon_root / 'car.png'),
}