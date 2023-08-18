"""Contains all text parsing functions which extract data"""
import re
import pandas as pd
import numpy as np
import logging

from .configs import config
from .configs import constants
from .plotting import default_rect

"""
The module begings with common and utility functions. At the end, the main
parsing functions follow, which will be loaded by a detection routine and
called automated. They all need the same API, currently this is:
    ```
    retrieved_data, total_price = parse_receipt_NAME(data, pats, pattern, ax=None)
    ```
where `data` is extracted data returned from the receipt class, `pats` is a
dict with a set of regexp parsing patterns, `pattern` is the `str` identifier
of the current patternset and `ax` is optional matplotlib axes used for
displaying rectangles.
"""
logger = logging.getLogger(__package__)


_retrieved_data_template = pd.DataFrame(
    columns=constants._MANDATORY_COLS)


def _flip_tax_class(retrieved_data, tc_inp1=1, tc_inp2=2):
    """
    Flips tax class, usually from 1 to 2 which is the way that is needed for
    `ger` receipts, especiallly ALDI.

    Parameters
    ----------
    retrieved_data : `pd.DataFrame`
        Input df.
    tc_inp1 : `int`, optional
        Switch value 1. The default is 1.
    tc_inp2 : `int`, optional
        Switch value 2. The default is 2.

    Returns
    -------
    retrieved_data : `pd.DataFrame`
        Output df with switched tax.
    """
    is_from = retrieved_data['TaxClass'] == tc_inp1
    is_to = retrieved_data['TaxClass'] == tc_inp2
    retrieved_data.loc[is_from, 'TaxClass'] = tc_inp2
    retrieved_data.loc[is_to, 'TaxClass'] = tc_inp1

    return retrieved_data


def get_vendor(raw_text):
    """
    Extracts vendor information from raw text.

    Parameters
    ----------
    raw_text : `str`
        Tesseract raw text

    Returns
    -------
    `tuple`
        Tuple with literal vendor name and the best fiitin set of parsing
        patterns.
    """
    for rec_t in config.receipt_types.keys():
        check_strings = [rec_t] + config.receipt_aliases.get(rec_t, [])
        this_check = any([re.search(rf'([\b_]*?{cs:s}|{cs:s}[_\b])', raw_text, re.IGNORECASE) is not None
                          for cs in check_strings])

        if this_check:
            patterns = config.receipt_types[rec_t]
            logger.debug(f'Vendor found: {rec_t}')
            return rec_t, patterns

    logger.debug('No vendor found, using general')
    return 'General', 'gen'


def get_date(raw_text, pattern):
    """
    Extracts date from tesseract raw text.

    Parameters
    ----------
    raw_text : `str`
        Tesseract raw text
    pattern : `re.compile`
        Precompiled pattern to detect a valid date.

    Returns
    -------
    `pd.Datetime`
        Date or `None` if no date was found.
    """
    date = pattern.search(raw_text)
    if date is not None:
        date = date.group(0).replace('_', '').replace('/', '.').replace(',', '.')
        try:
            date = pd.to_datetime(date, format='%d.%m.%Y')
        except ValueError:
            date = pd.to_datetime(date, format='%d.%m.%y')

    return date


def get_patterns(pattern, lang):
    """
    Combines language general and vendor specific patterns, prioritizing the
    latter, into a single pattern set.

    Parameters
    ----------
    pattern : `str`
        Vendor pattern identifier
    lang : `str`
        Pattern language

    Returns
    -------
    `dict`
        Patterns in a dict which are all `re.compile()` objects
    """
    if pattern == 'simple':
        logger.debug('Using simple patterns')
        return constants._patterns['simple']

    pats = constants._patterns['gen' + '_' + lang]
    try:
        pats.update(constants._patterns[pattern + '_' + lang])
    except KeyError:
        logger.info(f'No additional patterns found for {pattern:s}')
    return pats


def fill_missing_data(retrieved_data):
    """
    Fills misssing elements in a dataset using basic math.

    Parameters
    ----------
    retrieved_data : `pd.DataFrame`
        The input dataframe, parsed data from a parser.

    Returns
    -------
    `pd.DataFrame`
        Input data with nans replaced if possible.
    """
    units_nan = retrieved_data['Units'].isna()
    retrieved_data.loc[units_nan, 'Units'] = (
        retrieved_data.loc[units_nan, 'Price'] /
        retrieved_data.loc[units_nan, 'PricePerUnit'])

    retrieved_data['Units'] = retrieved_data['Units'].fillna(1)

    ppu_nan = retrieved_data['PricePerUnit'].isna()
    retrieved_data.loc[ppu_nan, 'PricePerUnit'] = (
        retrieved_data.loc[ppu_nan, 'Price'] /
        retrieved_data.loc[ppu_nan, 'Units'])

    p_nan = retrieved_data['Price'].isna()
    retrieved_data.loc[p_nan, 'Price'] = (
        retrieved_data.loc[p_nan, 'PricePerUnit'] *
        retrieved_data.loc[p_nan, 'Units'])

    return retrieved_data


##################
# Parser, selection dict at the end
##################
def parse_receipt_general_deu(data, pats, pattern, ax=None):
    """Basic general application parser for *deu*, signature see at the top"""
    retrieved_data = _retrieved_data_template.copy()
    # First item is usually first price, if not let it 0 so get everything
    first_item = 0
    first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()

    # Find the last row, before so this can be better applied with different
    # vendors. Extract final price. DM is very annoying with different discount
    # types and totals.
    total_price = 0
    if pattern == 'dm':
        # Are there mult. discounts?:
        last_line = data['text'].str.extract(
            r'(zu.*?zahlender.*?betrag)', re.IGNORECASE).first_valid_index()
        if last_line is not None:
            matcher = re.compile(r'\d{1,3},\d{2,3}', re.IGNORECASE)
        else:
            last_line = data['text'].str.extract(
                pats['total_sum_pattern']).first_valid_index()
            matcher = pats['total_sum_pattern']

        try:
            total_price = float(
                matcher.search(data.iloc[last_line]['text']).group(0).replace(',', '.').replace('_', ''))
            logger.debug(f'Found total price: {total_price:.2f}')
        except (ValueError, IndexError, TypeError):
            logger.warning('No total price detected')
            last_line = -1

    # This works for the general case
    else:
        last_line = data['text'].str.extract(
            pats['total_sum_pattern']).first_valid_index()

        if last_line is None:
            last_line = data.index[-1]

        try:
            total_price = float(
                pats['total_sum_pattern'].search(data.loc[last_line, 'text']
                                                 ).group(0).replace(',', '.').replace('_', ''))
            logger.debug(f'Found total price @ line: {total_price:.2f} @ {last_line:d}')
        except (ValueError, AttributeError):  # Either no match or no valid conversion
            logger.warning('No total price')

    # Initialize variables
    this_row_exists = False
    discount = 0
    unused_lines = []

    # Parse line by line and see what can be classified
    logger.debug(f' Searching from line {first_item:d} to {last_line:d}')
    for _, group in data[first_item:last_line].iterrows():
        has_price, has_weight, has_mult = False, False, False
        this_line = group['text']
        logger.debug(f'Analyzing: {this_line:s}')

        # Is there a price with tax class?
        if (re_res := pats['price_with_class'].search(this_line)) is not None:
            price, tax_class = re_res.group(1).replace('_', ''), re_res.group(2)

            try:
                price = float(price.replace(',', '.'))
            except ValueError:
                price = 0.

            tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2'))
            has_price = True
            logger.debug(f'Normal item price @ tax class {price:.2f} @ {tax_class:d}')

        # Is there a kg price, e.g. weight multiplier (then skip normal mult.)
        if (re_res := pats['weight_pattern'].search(this_line)) is not None:
            price_per_unit = float(re_res.group(0).replace(',', '.'))
            try:
                amount = float(
                    pats['amount_in_weight'].search(this_line).group(0).replace(',', '.'))
            except (ValueError, AttributeError):
                amount = 0

            has_weight = True
            logger.debug(f'Found weight: {amount:.3f} x {price_per_unit:.2f}')

        # If no weight, is there a multiplier?
        elif (re_res := pats['mult_pattern'].search(this_line)) is not None:
            # Again DM seems to be special
            if pattern == 'dm':
                re_res = pats['mult_pattern'].findall(this_line)
                if len(re_res) > 1:  # This catches stupid lines with e.g. .4x in text
                    try:
                        amount = float(re_res[0][0].replace(',', '.'))
                        price_per_unit = float(re_res[1][1].replace(',', '.').replace('_', ''))
                    except ValueError:
                        amount = 0
                        price_per_unit = 0

                    has_mult = True
                    logger.debug(f'Found weight: {amount:.3f} x {price_per_unit:.2f}')

            # And the general case
            else:
                try:
                    price_per_unit = float(re_res.group(0).replace(',', '.'))
                except ValueError:
                    price_per_unit = 0

                has_mult = True
                logger.debug(f'Found mult: {price_per_unit:.2f}')

        # Match discounts, currently only DM since there are a lot of coupons!
        if pattern == 'dm':
            if (re_res := pats['negative_price'].search(this_line)) is not None:
                try:
                    discount += float(re_res.group(0).replace(',', '.'))
                except ValueError:
                    logger.warning("Can't convert discount in DM receipt")
                continue

        # Analysis done, now extract and sort the data, this is the most
        # critical part and, as the search above, vendor specific!
        if not (has_price or has_mult or has_weight):
            unused_lines.append(this_line)
            continue

        # Has mult, e.g. weight (before item): pre-create row and set flag
        # Mult and weight cant occur together if the code above works!
        # Real and Rewe places mult after item: look behind
        if has_mult and not has_price:
            if pattern == 'real':
                logger.debug('Real look behind')
                retrieved_data.loc[
                    retrieved_data.index[-1], ['PricePerUnit']] = price_per_unit
            elif pattern == 'rewe':
                logger.debug('Rewe look behind')
                retrieved_data.loc[
                    retrieved_data.index[-1], ['PricePerUnit']] = price_per_unit
            else:
                retrieved_data = pd.concat(
                    [retrieved_data, pd.DataFrame({
                        'PricePerUnit': price_per_unit,
                    }, index=[0])],
                    ignore_index=True)
                this_row_exists = True

        # Found weight but no price with tax class: Lookbehind and assemble
        if has_weight and not has_price:
            retrieved_data.loc[
                retrieved_data.index[-1], ['Units', 'PricePerUnit']] = [amount, price_per_unit]

        # Found weight and price - this is a style where the name was in the row
        # before but not matched (get it from unused_lines). This is Rewe receipt
        elif has_weight and has_price:
            # There is a chance that the first line is a weight line and thus
            # the actual name was in first_item - 1 this needs to be handled:
            if not unused_lines:
                logger.debug(
                    'Catching a possible first item with weight, appending: '
                    f"{data.iloc[first_item - 1]['text']}")
                unused_lines.append(data.iloc[first_item - 1]['text'])
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': -1,
                    'Name': unused_lines[-1].replace('_', ' '),
                    'Price': price,
                    'TaxClass': tax_class,
                    'PricePerUnit': price_per_unit,
                    'Units': amount
                }, index=[0])],
                ignore_index=True)

        # Price and mult in a singleline: DM
        if has_price and has_mult:
            article_data = pats['valid_article_pattern_mult'].search(this_line).group(0).split('_')
            article_name = ' '.join([art for art in article_data if art])
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': -1,
                    'Name': article_name,
                    'Price': price,
                    'TaxClass': tax_class,
                    'Units': amount,
                    'PricePerUnit': price_per_unit
                }, index=[0])],
                ignore_index=True)

        # If this has a price and nothing else, then try to extract the name,
        # a possible article id and with that creating a new item
        if has_price and not (has_mult or has_weight):
            article_data = pats['valid_article_pattern'].match(this_line).group(0).split('_')
            if (re_res := re.match(r'\d{1,}', article_data[0])) is not None:
                article_number = int(re_res.group(0))
                article_name = ' '.join(article_data[1:]).strip()
            else:
                article_number = -1
                article_name = ' '.join(article_data).strip().lower().title()
            logger.debug(f'Final article: {article_number:d}, {article_name:s}')

            # Lookahead from before if price was missing for a mult line
            if this_row_exists:
                retrieved_data.loc[retrieved_data.index[-1],
                                   ['ArtNr', 'Name', 'Price', 'TaxClass']] = [
                                       article_number, article_name, price, tax_class]
                this_row_exists = False
            else:
                retrieved_data = pd.concat(
                    [retrieved_data, pd.DataFrame({
                        'ArtNr': article_number,
                        'Name': article_name,
                        'Price': price,
                        'TaxClass': tax_class
                    }, index=[0])],
                    ignore_index=True)

        # Heavy lifting done, phew! Now just plot if this was valid
        # Plot box if this line is a valid price around the full line
        if has_price and 'left' in group and ax is not None:
            default_rect(group, ax)

    # Add a discount
    if discount != 0:
        logger.debug(f'Discount: {discount:.2f}')
        retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'ArtNr': -1,
                'Name': 'Discount',
                'Price': discount,
                'TaxClass': 0,
                'Units': 1,
                'PricePerUnit': discount
            }, index=[0])],
            ignore_index=True)

    return retrieved_data, total_price


def parse_receipt_unverpackt(data, pats, pattern, ax=None):
    """Parser for *deu* and store *Unverpackt*, signature see at the top"""
    retrieved_data = _retrieved_data_template.copy()
    total_price = 0
    line_buffer = []
    # First item is usually first price - 2
    first_item = 0
    first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()
    first_item = max(0, first_item - 2)
    for _, group in data[first_item:].iterrows():
        this_line = group['text']
        logger.debug(f'Analyzing: {this_line:s}')

        # Is there a price with tax class? Then the line before is ArtNr
        # and the one before that name
        if (re_res := pats['price_with_class'].search(this_line)) is not None:
            price, tax_class = re_res.group(1).replace('_', ''), re_res.group(2)

            try:
                price = float(price.replace(',', '.'))
            except ValueError:
                price = 0.

            tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2'))
            article_number = int(pats['article_number'].search(line_buffer[-1]).group(0))
            article_name = line_buffer[-2].replace('_', ' ')

            logger.debug(
                f'Item: {article_number:d}, {article_name:s}, {price:.2f} @ {tax_class:d}')

            # extract units and price per unit
            weight_info = pats['mult_pattern'].findall(this_line)
            try:
                amount = float(weight_info[0].replace(',', '.'))
                price_per_unit = float(weight_info[1].replace(',', '.'))
            except ValueError:
                amount = 0
                price_per_unit = 0

            line_buffer = []

            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': article_number,
                    'Name': article_name,
                    'Price': price,
                    'TaxClass': tax_class,
                    'Units': amount,
                    'PricePerUnit': price_per_unit
                }, index=[0])],
                ignore_index=True)

            if 'left' in group and ax is not None:
                default_rect(group, ax)

        line_buffer.append(this_line)

        # Finally, is there a final price? If so break the loop
        if (re_res := pats['total_sum_pattern'].search(this_line)) is not None:
            try:
                total_price = float(re_res.group(0).replace(',', '.').replace('_', ''))
                logger.debug(f'Found total price: {total_price:.2f}')
                break
            except ValueError:
                logger.warning('No Total Price found!')

    return retrieved_data, total_price


def parse_receipt_raiff(data, pats, pattern, ax=None):
    """Parser for *deu* and store *Raiffeisen*, signature see at the top"""
    def _clear_name(this_line):
        start = this_line.find('(ST)')
        if start != -1:
            start = start + 4
        else:
            start = 0
        name = pats['valid_article_pattern'].search(this_line).group(0)  # valid art ptn
        if name is not None:
            name = name[start:].replace('_', ' ').strip()
        return name

    retrieved_data = _retrieved_data_template.copy()
    total_price = 0
    line_buffer = []

    first_item = 0
    first_item = data['text'].str.extract(r'([\dI]_[xX])').first_valid_index()

    for _, group in data[first_item:].iterrows():
        this_line = group['text']
        has_mult, has_price, add_data = False, False, False
        logger.debug(f'Analyzing: {this_line:s}')
        # Is there a price with tax class? Is the amount 1?
        if (re_res := pats['price_with_class'].search(this_line)) is not None:
            price, tax_class = re_res.group(1).replace('_', ''), re_res.group(2)

            try:
                price = float(price.replace(',', '.'))
            except ValueError:
                price = 0.

            tax_class = int(tax_class.upper().replace('A', '1').replace('B', '2').replace('I', '1'))

            has_price = True
            logger.debug(f'Article: {price:.2f} @ {tax_class:d}')

            # Now get the count if there, else this is a sum line
            if (re_res := re.search(r'^[I\d]{1,2}_*?[xX]', this_line)) is not None:
                try:
                    amount = int(re_res.group(0).split('_')[0].replace('I', '1'))
                except ValueError:
                    amount = 1
                ppu = price

            else:
                if (re_res := pats['mult_pattern'].search(this_line)) is not None:
                    try:
                        amount = int(re_res.group(0).replace('_', ''))
                    except ValueError:
                        amount = 1
                    if (re_res := pats['mult_price'].search(this_line)) is not None:
                        try:
                            ppu = float(re_res.group(0).replace('_', '').replace(',', '.'))
                        except ValueError:
                            ...

                has_mult = True
                logger.debug(f'Multiplier pattern: {amount:d} x {ppu:.2f}')

        # normal line
        if has_price and not has_mult:
            art_name = _clear_name(this_line)
            add_data = True

        # Data line, name from buffer
        if has_price and has_mult:
            art_name = _clear_name(line_buffer[-1])
            add_data = True

        # Line before mult
        elif not has_price:
            line_buffer.append(this_line)

        if add_data:
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': -1,
                    'Name': art_name,
                    'Price': price,
                    'TaxClass': tax_class,
                    'Units': amount,
                    'PricePerUnit': ppu
                }, index=[0])],
                ignore_index=True)

        if add_data and 'left' in group and ax is not None:
            default_rect(group, ax)

        if (re_res := pats['total_sum_pattern'].search(this_line)) is not None:
            try:
                total_price = float(re_res.group(0).replace(',', '.').replace('_', ''))
                logger.debug(f'Found total price: {total_price:.2f}')
                break
            except ValueError:
                logger.warning('No total price detected')

    return retrieved_data, total_price


def parse_receipt_general_fra(data, pats, pattern, ax=None):
    """Basic general application parser for *fra*, signature see at the top"""
    retrieved_data = _retrieved_data_template.copy()
    # First item is usually first price, if not let it 0 so get everything
    first_item = 0
    first_item = data['text'].str.extract(pats['simple_price_pattern']).first_valid_index()

    # Find the last row, before so this can be better applied with different
    # vendors. Extract final price. DM is very annoying with different discount
    # types and totals.
    total_price = 0

    last_line = data['text'].str.extract(
        pats['total_sum_pattern']).first_valid_index()

    if last_line is None:
        last_line = data.index[-1]

    try:
        total_price = float(
            pats['total_sum_pattern'].search(data.loc[last_line, 'text']
                                             ).group(0).replace(',', '.').replace('_', ''))
        logger.debug(f'Found total price @ line: {total_price:.2f} @ {last_line:d}')
    except (ValueError, AttributeError):  # Either no match or no valid conversion
        logger.warning('No total price detected')

    # Parse line by line and see what can be classified
    logger.debug(f' Searching from line {first_item:d} to {last_line:d}')
    for _, group in data[first_item:last_line].iterrows():
        this_line = group['text']
        logger.debug(f'Analyzing: {this_line:s}')

        # Skip sub totals
        if 'total' in this_line.lower():
            logger.debug('Skipping Subtotal Item')
            continue

        # is there a mult?
        if (re_res := pats['amount_pattern'].search(this_line)) is not None:
            try:
                amount = float(re_res.group(0).replace(',', '.'))
            except ValueError:
                amount = np.nan

            try:
                price_per_unit = float(pats['simple_price_pattern'].search(this_line).group(0).replace(',', '.'))
            except ValueError:
                price_per_unit = np.nan

            logger.debug(f'Multiplier found: {amount:.2f} x {price_per_unit:.2f}')
            retrieved_data.loc[
                retrieved_data.index[-1], ['Units']] = amount
            retrieved_data.loc[
                retrieved_data.index[-1], ['PricePerUnit']] = price_per_unit
            continue

        # Is this a valid line?
        if (re_res := pats['valid_article_pattern'].search(this_line)) is not None:

            try:
                price = float(re_res.group(3).replace(',', '.'))
            except ValueError:
                price = 0.

            try:
                tax_class = int(re_res.group(1))
            except ValueError:
                tax_class = 0

            art_name = re_res.group(2).replace('_', ' ').strip()

            logger.debug(f'Normal item: {art_name:s}, {price:.2f} @ {tax_class:d}')
            retrieved_data = pd.concat(
                [retrieved_data, pd.DataFrame({
                    'ArtNr': -1,
                    'Name': art_name,
                    'Price': price,
                    'TaxClass': tax_class,
                    'PricePerUnit': np.nan,
                    'Units': 1
                }, index=[0])],
                ignore_index=True)

            if 'left' in group and ax is not None:
                default_rect(group, ax)

    return retrieved_data, total_price


def parse_receipt_simple(data, pats, pattern, ax=None):
    """Most basic parser - this is a language unspecific fallback"""
    currency = config.options['currency'].strip()
    logger.debug(f'Most basic parser with currency: {currency}')
    retrieved_data = _retrieved_data_template.copy()

    # Precompile, format fails with complex quantifiers
    simple_price_pt = pats['simple_price_pattern'].replace('CURRENCY', currency)
    article_name_pt = pats['article_name_pattern'].replace('CURRENCY', currency)
    simple_price_pt = re.compile(simple_price_pt)
    article_name_pt = re.compile(article_name_pt)

    # First item is usually first price, if not let it 0 so get everything
    first_item = 0
    first_item = data['text'].str.extract(simple_price_pt).first_valid_index()

    # Find the last row, before so this can be better applied with different
    # vendors. Extract final price. DM is very annoying with different discount
    # types and totals.
    total_price = 0

    last_line = data['text'].str.extract(
        pats['total_sum_line']).first_valid_index()

    if last_line is None:
        last_line = data.index[-1]

    try:
        total_price = float(
            simple_price_pt.search(
            data.loc[last_line, 'text']).group(0).replace(',', '.').replace('_', ''))
        logger.debug(f'Found total price @ line: {total_price:.2f} @ {last_line:d}')
    except (ValueError, AttributeError):  # Either no match or no valid conversion
        logger.warning('No total price detected')

    # Parse line by line and see what can be classified
    logger.debug(f' Searching from line {first_item:d} to {last_line:d}')
    for _, group in data[first_item:last_line].iterrows():
        this_line = group['text']

        if (re_res := simple_price_pt.search(this_line)) is not None:
            try:
                price = float(re_res.group(0).replace(',', '.'))
            except ValueError:
                price = 0.

            try:
                re_res = article_name_pt.search(this_line)
                art_name = re_res.group(1).replace('_', ' ').strip()
            except Exception:
                logger.debug('Cant match article name')
                art_name = 'none'

            retrieved_data = pd.concat(
            [retrieved_data, pd.DataFrame({
                'ArtNr': -1,
                'Name': art_name,
                'Price': price,
                'TaxClass': 0,
                'Units': 1,
                'PricePerUnit': np.nan
            }, index=[0])],
            ignore_index=True)

            if 'left' in group and ax is not None:
                default_rect(group, ax)

    return retrieved_data, total_price


_av_parser = {
    'unverpackt': parse_receipt_unverpackt,
    'raiff': parse_receipt_raiff,
    'gen_deu': parse_receipt_general_deu,
    'gen_fra': parse_receipt_general_fra,
    'simple': parse_receipt_simple
}


def select_parser(patident, lang):
    """
    Returns the best fitting parser for a given pattern identifier and a
    selected language.
    """
    if patident in _av_parser:
        return _av_parser[patident]
    else:
        if f'gen_{lang}' in _av_parser:
            return _av_parser[f'gen_{lang}']
        else:
            logger.warning(
                'Not even a language specific parser available - falling '
                'back to super simple. Make sure at least your currency symbol '
                'is set!')
            return _av_parser['simple']
