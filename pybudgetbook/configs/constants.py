"""Containts package wide constants"""
import re
from pathlib import Path


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

_UI_LANG_SUPPORT = ['deu', 'eng', 'fra']

# Maps pattern with lang to set of regexp, general is always used (lang
# specific) and the rest is updated using `dict` update. Patterns are fairly
# complex and thus are not included in user config space.
_patterns = {
    'gen_deu': {'simple_price_pattern': re.compile(r'(\d{1,3}[,.]\d{2})'),
                'price_with_class': re.compile(r'(\d{1,3}[,.]\d{2,3}_*?)([AB12]|AW)(?:[x*]*?)$'),
                'mult_pattern': re.compile(r'((?<=[\W][xX*]_)\d{1,3}[,.]\d{2})'),
                'weight_pattern': re.compile(r'(\d{1,3}[,.]\d{1,3}(?=_EUR\/kg))', re.IGNORECASE),
                'valid_article_pattern': re.compile(r'(.*?(?=(\d{1,3}[,.]\d{2})))'),
                'amount_in_weight': re.compile(r'(\b\d{1,2}[,.]\d{1,3})'),
                'total_sum_pattern': re.compile(
                    r'((?<=total_eur.)\d{1,3}_*?[,.]_*?\d{2})|'
                    r'((?<=betrag_eur.)\d{1,3}_*?[,.]_*?\d{2})|'
                    r'((?<=summe_eur.)\d{1,3}_*?[,.]_*?\d{2})|'
                    r'((?<=total.)\d{1,3}_*?[,.]_*?\d{2})|'
                    r'((?<=betrag.)\d{1,3}_*?[,.]_*?\d{2})|'
                    r'((?<=summe.)\d{1,3}_*?[,.]_*?\d{2})',
                    re.IGNORECASE),
                'date_pattern': re.compile(
                    r'[0-3]\d[,.\/]_*?[0,1]\d[,.\/]_*?(2[0,1]\d{2}|\d{2})'),
                },
    'dm_deu': {'mult_pattern': re.compile(r'(\d{1,4}_*?(?=[xX*]))|((?<=[xX*])_*?\d{1,2}[,.]\d{1,3})'),
               'valid_article_pattern_mult': re.compile(
                   r'(?=_[a-zA-Z]).*?(?=_\d{1,2}[,.]\d{1,3})'),
               'negative_price': re.compile(r'-\d{1,3}[,.]\d{1,2}'),
               'total_sum_pattern': re.compile(
                   r'((?<=\bsumme_eur.)\d{1,3}_*?[,.]_*?\d{2})',
                   re.IGNORECASE)
               },
    'unverpackt_deu': {
        'article_number': re.compile(r'\d{1,}'),
        'mult_pattern': re.compile(r'\d{1,2}[,.]\d{1,3}'),
        'total_sum_pattern': re.compile(r'((?<=summe.)\d{1,3}_*?[,.]_*?\d{2})', re.IGNORECASE),
    },
    'real_deu': {},  # inherits all, but the flag is needed for sorting
    'rewe_deu': {'mult_pattern': re.compile(r'((?<=[xX*]_)\d{1,3}[,.]\d{2})')},  # small catch due to sometimes bad mults
    'rewe_delivery_deu': {'simple_price_pattern': re.compile(r'(\d{1,3}[,.]\d{2}[ _]*?€)'),
                          'article_pattern': re.compile(r'_(\d)_([AB]|A\/B)_(\d{1,3}[,.]\d{1,2})[ _]*?€', re.IGNORECASE),
                          'weight_pattern': re.compile(r'_(\d{1,4}g|kg)_([AB]|A\/B)_(\d{1,3}[,.]\d{1,2})[ _]*?€\/kg', re.IGNORECASE),
                          'total_sum_pattern': re.compile(r'Summe[ _]*?(\d{1,3}[,.]\d{2})[ _]*?€', re.IGNORECASE)},
    'tank_deu': {'price_with_class_2': re.compile(r'(\d{1,3}[,.]\d{2,3}(?=_*?[EUR]{0,3}-[AB12]))')
                 },
    'raiff_deu': {'price_with_class': re.compile(r'(\d{1,3}[,.]\d{2,3}_*?)([AB12]|AW)(?:[x*]*?)$'),
                  'mult_pattern': re.compile(r'(\d{1,3}(?=[xX*]))'),
                  'mult_price': re.compile(r'((?<=[xX*])_*?\d{1,3}[.,]\d{1,2})'),
                  'valid_article_pattern': re.compile(r'(.*?(?=(\d{1,3}[,.]\d{2})))'),
                  'total_sum_pattern': re.compile(r'((?<=summe.))_*?\d{1,3}_*?[,.]_*?\d{2}', re.IGNORECASE),
                  },
    'gen_fra': {'simple_price_pattern': re.compile(r'(\d{1,3}[,.]\d{1,2}(?=€)?)'),
                'valid_article_pattern': re.compile(r'(^\d(?!\d))(?:[_])*([^_].*?[^_])(?:_)*(\d{1,3}[,.]\d{1,2}(?=€)?)'),
                'amount_pattern': re.compile(r'\d{1,2}(?=_[xX]_)'),
                'total_sum_pattern': re.compile(
                    r'((?<=payer.)\d{1,3}_*?[,.]_*?\d{1,2})|'
                    r'((?<=total . payer.)\d{1,3}_*?[,.]_*?\d{1,2})',
                    re.IGNORECASE),
                'date_pattern': re.compile(
                    r'[0-3]\d[,.\/]_*?[0,1]\d[,.\/]_*?(2[0,1]\d{2}|\d{2})'),
                },
    'simple': {'simple_price_pattern': r'(\d{1,3}[,.]\d{2}_*?(?=CURRENCY))',
                'total_sum_line': re.compile(
                    '(total|betrag|summe|sum|payer|amount|totale)',
                    re.IGNORECASE),
                'article_name_pattern': r'(.*?)(\d{1,3}[.,|]\d{1,2}[_ ]*CURRENCY).*',
                'date_pattern': re.compile(
                    r'[0-3]{0,1}\d[,.\/]_*?[0,1]{0,1}\d[,.\/]_*?(2[0,1]\d{2}|\d{2})'),
                },
}

# Icons to use for group display
_icon_root = Path(__file__).parent.parent / 'img' / 'groups'
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

    'Groceries': str(_icon_root / 'general.png'),
    'Dairy': str(_icon_root / 'dairy.png'),
    'Vegetables': str(_icon_root / 'veggies.png'),
    'Fruits': str(_icon_root / 'fruit.png'),
    'Berries': str(_icon_root / 'berry.png'),
    'Ham & Cheese': str(_icon_root / 'sausage.png'),
    'Candy': str(_icon_root / 'sweets.png'),
    'Beverages': str(_icon_root / 'drinks.png'),
    'Alcoholics': str(_icon_root / 'alco.png'),
    'Household': str(_icon_root / 'house_gen.png'),
    'Toiletries': str(_icon_root / 'drugstore.png'),
    'Kids': str(_icon_root / 'kids.png'),
    'Bakery': str(_icon_root / 'bakery.png'),
    'Automotive': str(_icon_root / 'car.png'),

    'Alimentaires Base': str(_icon_root / 'general.png'),
    'Produits laitiers': str(_icon_root / 'dairy.png'),
    'Légumes': str(_icon_root / 'veggies.png'),
    'Fruits': str(_icon_root / 'fruit.png'),
    'Baies': str(_icon_root / 'berry.png'),
    'Charcuterie / Fromage': str(_icon_root / 'sausage.png'),
    'Douceurs': str(_icon_root / 'sweets.png'),
    'Boissons': str(_icon_root / 'drinks.png'),
    'Alcool': str(_icon_root / 'alco.png'),
    'Entretien de la maison': str(_icon_root / 'house_gen.png'),
    'Droguerie': str(_icon_root / 'drugstore.png'),
    'Enfants': str(_icon_root / 'kids.png'),
    'Boulangerie': str(_icon_root / 'bakery.png'),
    'Automobile': str(_icon_root / 'car.png'),
}
