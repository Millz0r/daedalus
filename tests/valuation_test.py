import json
import sys
import unittest

from daedalus.valuation import valuation, service
from daedalus.xlstransform import transforms
from decimal import Decimal

from mock import patch
from utils import valuation_workbook, valuation_workbook_two, valuation_solution, valuation_workbook_path

class CalculateOccupancyTest(unittest.TestCase):
    def test_good(self):
        current_leases = Decimal(10)
        units = Decimal(5)
        self.assertEqual(valuation._calculate_occupancy(current_leases, units), Decimal(2))

    def test_zero_units(self):
        current_leases = Decimal(10)
        units = Decimal(0)
        self.assertEqual(valuation._calculate_occupancy(current_leases, units), 0)

    def test_zero_leases(self):
        current_leases = Decimal(0)
        units = Decimal(2)
        self.assertEqual(valuation._calculate_occupancy(current_leases, units), 0)

    def test_bad_current_leases(self):
        current_leases = 'an ape'
        units = Decimal(2)
        with self.assertRaises(AssertionError):
            valuation._calculate_occupancy(current_leases, units)

    def test_bad_units(self):
        current_leases = Decimal(10)
        units = 'a flock of jellyfish'
        with self.assertRaises(AssertionError):
            valuation._calculate_occupancy(current_leases, units)

class CalculateRentBaselineTest(unittest.TestCase):
    def test_good(self):
        monthly_rents = Decimal(100)
        occupancy = Decimal('0.8')
        self.assertEqual(valuation._calculate_rent_baseline(monthly_rents, occupancy), Decimal(960))

    def test_zero_monthly_rents(self):
        monthly_rents = Decimal(0)
        occupancy = Decimal('0.8')
        self.assertEqual(valuation._calculate_rent_baseline(monthly_rents, occupancy), Decimal(0))

    def test_zero_occupancy(self):
        monthly_rents = Decimal(100)
        occupancy = Decimal(0)
        self.assertEqual(valuation._calculate_rent_baseline(monthly_rents, occupancy), Decimal(0))

    def test_bad_monthly_rents(self):
        monthly_rents = 'darth vader'
        occupancy = Decimal('0.8')
        with self.assertRaises(AssertionError):
            valuation._calculate_rent_baseline(monthly_rents, occupancy)

    def test_bad_occupancy(self):
        monthly_rents = Decimal(100)
        occupancy = 'a dream cow'
        with self.assertRaises(AssertionError):
            valuation._calculate_rent_baseline(monthly_rents, occupancy)

class BipsOverTest(unittest.TestCase):
    def test_good(self):
        bips = Decimal(450)
        self.assertEqual(valuation._bips_over(bips), Decimal('1.0450'))

    def test_zero_bips(self):
        bips = Decimal(0)
        self.assertEqual(valuation._bips_over(bips), Decimal('1.0'))

    def test_bad_bips(self):
        bips = 'the letter z'
        with self.assertRaises(AssertionError):
            valuation._bips_over(bips)

class ListOfPremiumTest(unittest.TestCase):
    def test_good(self):
        list_of_deal_values = [Decimal(10), Decimal(20), Decimal(30)]
        total_value = Decimal(10)
        self.assertEqual(valuation._list_of_premium(list_of_deal_values, total_value), [Decimal('0.0'), Decimal('1.0'), Decimal('2.0')])

    def test_zero_list_of_deal_values(self):
        list_of_deal_values = [Decimal(0), Decimal(0), Decimal(30)]
        total_value = Decimal(10)
        self.assertEqual(valuation._list_of_premium(list_of_deal_values, total_value), [Decimal('-1.0'), Decimal('-1.0'), Decimal('2.0')])

    def test_zero_total_value(self):
        list_of_deal_values = [Decimal(10), Decimal(20), Decimal(30)]
        total_value = Decimal(0)
        self.assertEqual(valuation._list_of_premium(list_of_deal_values, total_value), [])

    def test_bad_list_of_deal_values(self):
        list_of_deal_values = 'a gaggle of selfies'
        total_value = Decimal(10)
        with self.assertRaises(AssertionError):
            valuation._list_of_premium(list_of_deal_values, total_value)

    def test_bad_total_value(self):
        list_of_deal_values = [Decimal(10), Decimal(20), Decimal(30)]
        total_value = 'a big number'
        with self.assertRaises(AssertionError):
            valuation._list_of_premium(list_of_deal_values, total_value)

class ListOfDealValueTest(unittest.TestCase):
    def test_good(self):
        list_of_ratios = [Decimal('1.1'), Decimal('1.2'), Decimal('1.3')]
        total_value = Decimal(10)
        self.assertEqual(valuation._list_of_deal_value(list_of_ratios, total_value), [Decimal(11), Decimal(12), Decimal(13)])

    def test_zero_list_of_ratios(self):
        list_of_ratios = [Decimal(0), Decimal('1.2'), Decimal('1.3')]
        total_value = Decimal(10)
        self.assertEqual(valuation._list_of_deal_value(list_of_ratios, total_value), [Decimal(0), Decimal(12), Decimal(13)])

    def test_zero_total_value(self):
        list_of_ratios = [Decimal('1.1'), Decimal('1.2'), Decimal('1.3')]
        total_value = Decimal(0)
        self.assertEqual(valuation._list_of_deal_value(list_of_ratios, total_value), [])

    def test_bad_list_of_ratios(self):
        list_of_ratios = 'this isn\'t a string.'
        total_value = Decimal(10)
        with self.assertRaises(AssertionError):
            valuation._list_of_deal_value(list_of_ratios, total_value)

    def test_bad_total_value(self):
        list_of_ratios = [Decimal('1.1'), Decimal('1.2'), Decimal('1.3')]
        total_value = 'pretty large number'
        with self.assertRaises(AssertionError):
            valuation._list_of_deal_value(list_of_ratios, total_value)

class ListOfProfitTest(unittest.TestCase):
    def test_good(self):
        list_of_deals = [Decimal(70), Decimal(300), Decimal(400)]
        baseline = Decimal(100)
        self.assertEqual(valuation._list_of_profit(list_of_deals, baseline), [Decimal(30.0), Decimal(-200.0), Decimal(-300.0)])

    def test_zero_list_of_deals(self):
        list_of_deals = [Decimal(0), Decimal(0), Decimal(400)]
        baseline = Decimal(100)
        self.assertEqual(valuation._list_of_profit(list_of_deals, baseline), [Decimal(100.0), Decimal(100.0), Decimal(-300.0)])

    def test_zero_total_value(self):
        list_of_deals = [Decimal(70), Decimal(300), Decimal(400)]
        baseline = Decimal(0)
        self.assertEqual(valuation._list_of_profit(list_of_deals, baseline), [Decimal('-70'), Decimal('-300.0'), Decimal('-400.0')])

    def test_bad_list_of_ratios(self):
        list_of_deals = 'this isn\'t a string.'
        baseline = Decimal(10)
        with self.assertRaises(AssertionError):
            valuation._list_of_profit(list_of_deals, baseline)

    def test_bad_total_value(self):
        list_of_deals = [Decimal(70), Decimal(300), Decimal(400)]
        baseline = 'Apes!'
        with self.assertRaises(AssertionError):
            valuation._list_of_profit(list_of_deals, baseline)

class ListOfGrossYieldTest(unittest.TestCase):
    def test_good(self):
        list_of_deals = [Decimal(200), Decimal(300), Decimal(400)]
        base_rents = Decimal(100)
        self.assertEqual(valuation._list_of_gross_yield(list_of_deals, base_rents), [Decimal('0.5'), Decimal(1) / Decimal(3), Decimal('0.25')])

    def test_zero_list_of_deals(self):
        list_of_deals = [Decimal(0), Decimal(0), Decimal(400)]
        base_rents = Decimal(100)
        self.assertEqual(valuation._list_of_gross_yield(list_of_deals, base_rents), [None, None, Decimal('0.25')])

    def test_zero_total_value(self):
        list_of_deals = [Decimal(70), Decimal(300), Decimal(400)]
        base_rents = Decimal(0)
        self.assertEqual(valuation._list_of_gross_yield(list_of_deals, base_rents), [Decimal(0), Decimal(0), Decimal(0)])

    def test_bad_list_of_ratios(self):
        list_of_deals = 'this isn\'t a string.'
        base_rents = Decimal(10)
        with self.assertRaises(AssertionError):
            valuation._list_of_gross_yield(list_of_deals, base_rents)

    def test_bad_total_value(self):
        list_of_deals = [Decimal(70), Decimal(300), Decimal(400)]
        base_rents = 'Apes!'
        with self.assertRaises(AssertionError):
            valuation._list_of_gross_yield(list_of_deals, base_rents)

class ListOfNoiTest(unittest.TestCase):
    def test_good(self):
        list_of_yields = [Decimal('0.075'), Decimal('0.12'), Decimal('0.18')]
        noi_percent = Decimal('0.55')
        self.assertEqual(valuation._list_of_noi(list_of_yields, noi_percent), [Decimal('0.04125'), Decimal('0.066'), Decimal('0.099')])

    def test_zero_list_of_deals(self):
        list_of_yields = [Decimal('-0.075'), Decimal(0)]
        noi_percent = Decimal('0.55')
        self.assertEqual(valuation._list_of_noi(list_of_yields, noi_percent), [Decimal('-0.04125'), Decimal('0')])

    def test_zero_total_value(self):
        list_of_yields = [Decimal('0.075'), Decimal('0.12'), Decimal('0.18')]
        noi_percent = Decimal(0)
        self.assertEqual(valuation._list_of_noi(list_of_yields, noi_percent), [Decimal(0), Decimal(0), Decimal(0)])

    def test_bad_list_of_ratios(self):
        list_of_yields = 'this isn\'t a string.'
        noi_percent = Decimal(10)
        with self.assertRaises(AssertionError):
            valuation._list_of_noi(list_of_yields, noi_percent)

    def test_bad_total_value(self):
        list_of_yields = [Decimal('0.075'), Decimal('0.12'), Decimal('0.18')]
        noi_percent = 'Apes!'
        with self.assertRaises(AssertionError):
            valuation._list_of_noi(list_of_yields, noi_percent)

class ListOfSurplusTest(unittest.TestCase):
    def test_good(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('0.03')
        target_irr = Decimal('0.12')
        self.assertEqual(valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr), [Decimal('-0.06'), Decimal('-0.03'), Decimal('0.0')])

    def test_zero_list_of_nois(self):
        list_of_nois = [Decimal('0.0'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('-0.03')
        target_irr = Decimal('0.12')
        self.assertEqual(valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr), [Decimal('-0.15'), Decimal('-0.09'), Decimal('-0.06')])

    def test_zero_return_factor(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0')
        return_coefficient = Decimal('0.03')
        target_irr = Decimal('0.12')
        self.assertEqual(valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr), [Decimal('-0.09'), Decimal('-0.09'), Decimal('-0.09')])

    def test_zero_return_coefficient(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('0')
        target_irr = Decimal('0.12')
        self.assertEqual(valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr), [Decimal('-0.09'), Decimal('-0.06'), Decimal('-0.03')])

    def test_zero_target_irr(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('0.03')
        target_irr = Decimal('0')
        self.assertEqual(valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr), [Decimal('0.06'), Decimal('0.09'), Decimal('0.12')])

    def test_bad_list_of_nois(self):
        list_of_nois = 'wrong'
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('0.03')
        target_irr = Decimal('0')
        with self.assertRaises(AssertionError):
            valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr)

    def test_bad_return_factor(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = 'wrong'
        return_coefficient = Decimal('0.03')
        target_irr = Decimal('0')
        with self.assertRaises(AssertionError):
            valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr)

    def test_bad_return_coefficient(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = 'wrong'
        target_irr = Decimal('0')
        with self.assertRaises(AssertionError):
            valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr)

    def test_bad_target_irr(self):
        list_of_nois = [Decimal('0.06'), Decimal('0.12'), Decimal('0.18')]
        return_factor = Decimal('0.5')
        return_coefficient = Decimal('0.03')
        target_irr = 'wrong'
        with self.assertRaises(AssertionError):
            valuation._list_of_surplus(list_of_nois, return_factor, return_coefficient, target_irr)

class ListOfCouponIrrTest(unittest.TestCase):
    def test_good(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.05'), Decimal('0.18')]
        return_factor = Decimal(2)
        return_coefficient = Decimal('0.05')
        self.assertEqual(valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient), [Decimal('0.2'), Decimal('0.15'), Decimal('0.41')])

    def test_zero_list_of_nois(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.0'), Decimal('0.18')]
        return_factor = Decimal(2)
        return_coefficient = Decimal('-0.05')
        self.assertEqual(valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient), [Decimal('0.1'), Decimal('-0.05'), Decimal('0.31')])

    def test_zero_return_factor(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.05'), Decimal('0.18')]
        return_factor = Decimal(0)
        return_coefficient = Decimal('0.05')
        self.assertEqual(valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient), [Decimal('0.05'), Decimal('0.05'), Decimal('0.05')])

    def test_zero_return_coefficient(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.05'), Decimal('0.18')]
        return_factor = Decimal(2)
        return_coefficient = Decimal('0')
        self.assertEqual(valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient), [Decimal('0.15'), Decimal('0.1'), Decimal('0.36')])

    def test_bad_list_of_nois(self):
        list_of_nois = 'bah'
        return_factor = Decimal(2)
        return_coefficient = Decimal('0.05')
        with self.assertRaises(AssertionError):
            valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient)

    def test_bad_return_factor(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.05'), Decimal('0.18')]
        return_factor = 'bah'
        return_coefficient = Decimal('0.05')
        with self.assertRaises(AssertionError):
            valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient)

    def test_bad_return_coefficient(self):
        list_of_nois = [Decimal('0.075'), Decimal('0.05'), Decimal('0.18')]
        return_factor = Decimal(2)
        return_coefficient = 'bah'
        with self.assertRaises(AssertionError):
            valuation._list_of_coupon_irr(list_of_nois, return_factor, return_coefficient)

class ListOfIrrTest(unittest.TestCase):
    def test_good(self):
        list_of_coupons = [Decimal('0.2'), Decimal('0.29'), Decimal('0.41')]
        hpa_factor = Decimal('1.0425')
        self.assertEqual(valuation._list_of_irr(list_of_coupons, hpa_factor), [Decimal('0.2425'), Decimal('0.3325'), Decimal('0.4525')])

    def test_zero_list_of_coupons(self):
        list_of_coupons = [Decimal('0.2'), Decimal('0'), Decimal('0.41')]
        hpa_factor = Decimal('0.9')
        self.assertEqual(valuation._list_of_irr(list_of_coupons, hpa_factor), [Decimal('0.1'), Decimal('-0.1'), Decimal('0.31')])

    def test_zero_hpa_factor(self):
        list_of_coupons = [Decimal('0.2'), Decimal('0.29'), Decimal('0.41')]
        hpa_factor = Decimal('0.0')
        self.assertEqual(valuation._list_of_irr(list_of_coupons, hpa_factor), [Decimal('-0.8'), Decimal('-0.71'), Decimal('-0.59')])

    def test_bad_list_of_coupons(self):
        list_of_coupons = 'arrrg'
        hpa_factor = Decimal('0.9')
        with self.assertRaises(AssertionError):
            valuation._list_of_irr(list_of_coupons, hpa_factor)

    def test_bad_hpa_factor(self):
        list_of_coupons = [Decimal('0.2'), Decimal('0.29'), Decimal('0.41')]
        hpa_factor = 'arrg'
        with self.assertRaises(AssertionError):
            valuation._list_of_irr(list_of_coupons, hpa_factor)

class TestValuation(unittest.TestCase):
    def test_good(self):
        read_as_xl = valuation_workbook_two()
        read_as_json = transforms.transform(read_as_xl)
        result = valuation.valuate(json.loads(read_as_json))
        self.assertIsInstance(read_as_json, basestring)

    def test_process_task(self):
        with patch('daedalus.valuation') as valuation_mock:
            valuation_mock.assert_called()
