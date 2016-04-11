'''Generates a valuation for a given portfolio.'''
from __future__ import division

import daedalus.exceptions
import decimal
import pandas

from daedalus.common.types import is_decimal, is_list_of_decimals

# Look up for Excel column name text
__COLUMN_LABEL__ = {
    'unit count': '# of Units',
    'lease count': '# of Leases', # Alternative label: # of Current Leases
    'valuation': 'Valuation',     # Alternative label: 2014Q3 Valuation
    'rent': 'Monthly Rent'        # Alternative label: Rent
}

# Industry rules of thumb
__EMPIRICAL_COST_FACTOR__ = decimal.Decimal('-0.035')
__EMPIRICAL_RETURN_FACTOR__ = decimal.Decimal('3.0')
__HPA_FACTOR__ = decimal.Decimal('1.0141')

def _calculate_occupancy(current_leases, units):
    '''Computes occupancy from total lease revenue and number of units.'''
    assert is_decimal(current_leases)
    assert is_decimal(units)

    return current_leases / units if units != 0 else 0

def _calculate_rent_baseline(monthly_rents, occupancy, month_in_year=12):
    '''Computes baseline annual revenue from total monthly rents including occupancy assumption.'''
    assert is_decimal(monthly_rents)
    assert is_decimal(occupancy)
    assert 1 <= month_in_year <= 12

    return monthly_rents * month_in_year * occupancy

def _bips_over(bips):
    '''Basis points over 100%.'''
    assert is_decimal(bips)

    return 1 + bips / decimal.Decimal(10000.0)

def _list_of_premium(list_of_deal_values, total_value):
    '''Calculate List of fractional premium (negative for discount) relative to total deal value.'''
    assert is_list_of_decimals(list_of_deal_values)
    assert is_decimal(total_value)

    if total_value == 0:
        return []
    return [(deal_value/total_value) - decimal.Decimal(1.0) for deal_value in list_of_deal_values]

def _list_of_deal_value(list_of_ratios, total_value):
    '''Calculate List of dollar values for deals given ratios and total valuation.'''
    assert is_list_of_decimals(list_of_ratios)
    assert is_decimal(total_value)

    if total_value == 0:
        return []
    return [(ratio * total_value) for ratio in list_of_ratios]

def _list_of_profit(list_of_deals, baseline):
    '''Calculate List of dollar profit versus baseline.'''
    assert is_list_of_decimals(list_of_deals)
    assert is_decimal(baseline)

    return [(baseline - deal_value) for deal_value in list_of_deals]

def _list_of_gross_yield(list_of_deals, base_rents):
    '''Calculate List of gross yields.'''
    assert is_list_of_decimals(list_of_deals)
    assert is_decimal(base_rents)

    return [(base_rents / deal) if deal != 0 else None for deal in list_of_deals]

def _list_of_noi(list_of_yields, noi_percent):
    '''Calculate List of Net Operating Incomes given yields for each deal and NOI percent.'''
    assert is_list_of_decimals(list_of_yields)
    assert is_decimal(noi_percent)

    return [(deal_yield * noi_percent) for deal_yield in list_of_yields]

def _list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr):
    '''Calculate List of surplus for deal list.'''
    assert is_list_of_decimals(list_of_nois)
    assert is_decimal(return_factor)
    assert is_decimal(return_coefficient)
    assert is_decimal(target_irr)

    return [(noi * return_factor) + return_coefficient - target_irr for noi in list_of_nois]

def _list_of_coupon_irr(list_of_nois, return_factor, return_coefficient):
    '''Calculate list of Coupon IRRs for deal list.'''
    assert is_list_of_decimals(list_of_nois)
    assert is_decimal(return_factor)
    assert is_decimal(return_coefficient)

    return [(noi * return_factor) + return_coefficient for noi in list_of_nois]

def _list_of_irr(list_of_coupons, hpa_factor):
    '''Calculate list of IRRs for deal list.'''
    assert is_list_of_decimals(list_of_coupons)
    assert is_decimal(hpa_factor)

    return [(coupon + hpa_factor - decimal.Decimal(1.0)) for coupon in list_of_coupons]

def _parse_incoming_data(data_as_json, deal_sheet_number=0, data_sheet_number=1):
    '''Pulls out the needed sheets from the JSON data.'''
    # parse the JSON for the data we need
    sheet_list = data_as_json['sheets']
    deal_sheet = sheet_list[deal_sheet_number]
    data_sheet = sheet_list[data_sheet_number]

    # pull each sheet into the appropriate dataframe
    data_frame = pandas.DataFrame(data=data_sheet['rows'], columns=data_sheet['columns'], dtype=decimal.Decimal)
    loan_frame = pandas.DataFrame(data=deal_sheet['rows'], columns=deal_sheet['columns'], dtype=decimal.Decimal)

    return data_frame, loan_frame

def _get_from_frame(key, loan_frame):
    '''Pulls a value from the dataframe for quick and easy access.'''
    try:
        return decimal.Decimal(loan_frame[key][0])
    except (KeyError, IndexError):
        raise daedalus.exceptions.BadDataFrameKey('Cannot find a value for: %r' % key)

def _build_offer_matrix(big_matrix=False):
    '''Formats the initial output dataframe.'''
    offer_names = ['At Valuation', 'Offer', 'Counter @ 8pct', 'Counter @ 6pct', 'Counter @ 4pct', 'Counter @ 475 bips']
    offer_over_valuation = [decimal.Decimal(value) for value in [1.0, 'NaN', 1.08, 1.06, 1.04, 1.0475]]
    if big_matrix:
        offer_names = ['At Valuation', 'Offer']
        offer_over_valuation = [decimal.Decimal(value) for value in [1.0, decimal.Decimal('NaN')]]
        for i in range(400, 710, 10):
            big_matrix_name = str(i) + " bips over"
            if i % 100 == 0:
                big_matrix_name = "plus " + str(i/100) + "percent"
            offer_names.append(big_matrix_name)
            offer_over_valuation.append(_bips_over(i))

    offer_data_set = zip(offer_names, offer_over_valuation)
    return pandas.DataFrame(data=offer_data_set, columns=['Offer Name', 'Offer Over Valuation'], dtype=decimal.Decimal)


def valuate(data_as_json, big_matrix=False):
    '''Main entrypoint of the valuator.

    data_as_json - the data as a JSON dict.
    big_matrix - boolean, create a full sensativity analysis using 400 bips to 700 bips in 10 bip increments, simple matrix otherwise.
    deal_sheet_number - zero-based integer index indicating which worksheet in the Excel file to pull deal parameters from.
    data_sheet_number - index indicating which worksheet to pull portfolio data from.
    '''

    data_frame, loan_frame = _parse_incoming_data(data_as_json, deal_sheet_number=0, data_sheet_number=1)

    # DEAL PARAMETERS
    current_offer = _get_from_frame('Current Offer', loan_frame)
    assumed_occupancy = _get_from_frame('Assumed Occupancy', loan_frame)
    operating_income_percent = _get_from_frame('Assumed Operating Income Percent', loan_frame)
    baseline_to_valuation = _get_from_frame('Baseline Real Value to Valuation', loan_frame)
    target_irr = _get_from_frame('Target IRR', loan_frame)

    # CALC BASIC METRICS

    # Rents and valuation total
    total_monthly_rents = decimal.Decimal(data_frame[__COLUMN_LABEL__['rent']].sum())
    baseline_annual_rents = _calculate_rent_baseline(total_monthly_rents, assumed_occupancy)
    total_current_valuation = decimal.Decimal(data_frame[__COLUMN_LABEL__['valuation']].sum())

    # Baseline real value
    baseline_real_value = total_current_valuation * baseline_to_valuation

    # Build offer matrix
    offer_matrix = _build_offer_matrix(big_matrix)
    offer_matrix['Deal Value'] = _list_of_deal_value(offer_matrix['Offer Over Valuation'], total_current_valuation)
    offer_matrix.loc[1, 'Deal Value'] = current_offer
    offer_matrix['Profit vs Baseline Value'] = _list_of_profit(offer_matrix['Deal Value'], baseline_real_value)
    offer_matrix['Gross Yield'] = _list_of_gross_yield(offer_matrix['Deal Value'], baseline_annual_rents)
    offer_matrix['NOI'] = _list_of_noi(offer_matrix['Gross Yield'], operating_income_percent)
    offer_matrix['Premium'] = _list_of_premium(offer_matrix['Deal Value'], total_current_valuation)
    offer_matrix['Surplus or Deficit'] = _list_of_surplus(offer_matrix['NOI'], __EMPIRICAL_RETURN_FACTOR__, __EMPIRICAL_COST_FACTOR__, target_irr)
    offer_matrix['Coupon IRR'] = _list_of_coupon_irr(offer_matrix['NOI'], __EMPIRICAL_RETURN_FACTOR__, __EMPIRICAL_COST_FACTOR__)
    offer_matrix['Total IRR'] = _list_of_irr(offer_matrix['Coupon IRR'], __HPA_FACTOR__)

    # Stupid hack to swap Decimal('NaN') for None because Pandas doesn't know that Decimal('NaN') is the same as np.nan
    offer_matrix['Offer Over Valuation'][1] = None

    return offer_matrix.to_json()
