from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, time, timedelta
from core.models import User, Transaction, Pharmacy, PharmacyOpeningHour, Mask

class PharmacyOpenAtTimeViewTests(APITestCase):
    def setUp(self):
        self.pharmacy1 = Pharmacy.objects.create(name="Pharmacy One", cash_balance=1000)
        self.pharmacy2 = Pharmacy.objects.create(name="Pharmacy Two", cash_balance=1500)

        # Opening hours for both pharmacies
        PharmacyOpeningHour.objects.create(
            pharmacy=self.pharmacy1,
            day_of_week="Tue",
            open_time=time(14, 0),
            close_time=time(18, 0)
        )
        PharmacyOpeningHour.objects.create(
            pharmacy=self.pharmacy2,
            day_of_week="Tue",
            open_time=time(6, 0),
            close_time=time(20, 0)
        )

    def test_valid_open_pharmacy_query(self):
        url = reverse('pharmacies-open')
        response = self.client.get(url, {'day': 'Tue', 'time': '15:00:00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [ph['id'] for ph in response.data]
        self.assertIn(self.pharmacy1.id, ids)
        self.assertIn(self.pharmacy2.id, ids)

    def test_only_one_pharmacy_open(self):
        url = reverse('pharmacies-open')
        response = self.client.get(url, {'day': 'Tue', 'time': '07:00:00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [ph['id'] for ph in response.data]
        self.assertIn(self.pharmacy2.id, ids)
        self.assertNotIn(self.pharmacy1.id, ids)

    def test_invalid_time_format(self):
        url = reverse('pharmacies-open')
        response = self.client.get(url, {'day': 'Tue', 'time': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_params_returns_all(self):
        url = reverse('pharmacies-open')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class PharmacyMaskListViewTests(APITestCase):
    def setUp(self):
        self.pharmacy = Pharmacy.objects.create(name="Mask Store", cash_balance=2000)
        self.mask1 = Mask.objects.create(pharmacy=self.pharmacy, name="N95", price=15.00)
        self.mask2 = Mask.objects.create(pharmacy=self.pharmacy, name="Surgical", price=5.00)
        self.mask3 = Mask.objects.create(pharmacy=self.pharmacy, name="Cloth", price=8.00)

    def test_get_all_masks_unsorted(self):
        url = reverse('pharmacy-masks', kwargs={'pharmacy_id': self.pharmacy.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_sorted_by_name_asc(self):
        url = reverse('pharmacy-masks', kwargs={'pharmacy_id': self.pharmacy.id})
        response = self.client.get(url, {'sort_by': 'name'})
        names = [m['name'] for m in response.data]
        self.assertEqual(names, sorted(names))

    def test_sorted_by_price_desc(self):
        url = reverse('pharmacy-masks', kwargs={'pharmacy_id': self.pharmacy.id})
        response = self.client.get(url, {'sort_by': '-price'})
        prices = [float(item['price']) for item in response.data]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_invalid_sort_field_returns_400(self):
        url = reverse('pharmacy-masks', kwargs={'pharmacy_id': self.pharmacy.id})
        response = self.client.get(url, {'sort_by': 'unknown'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PharmaciesMaskCountFilterViewTests(APITestCase):
    def setUp(self):
        self.pharmacy1 = Pharmacy.objects.create(name="Pharma A", cash_balance=500)
        self.pharmacy2 = Pharmacy.objects.create(name="Pharma B", cash_balance=700)
        self.pharmacy3 = Pharmacy.objects.create(name="Pharma C", cash_balance=900)

        # Pharma A: 3 masks at $10
        for _ in range(3):
            Mask.objects.create(pharmacy=self.pharmacy1, name="Basic Mask", price=10.00)

        # Pharma B: 5 masks at $25
        for _ in range(5):
            Mask.objects.create(pharmacy=self.pharmacy2, name="Premium Mask", price=25.00)

        # Pharma C: 2 masks at $5
        for _ in range(2):
            Mask.objects.create(pharmacy=self.pharmacy3, name="Cheap Mask", price=5.00)

    def test_pharmacies_with_mask_count_greater_than_3_in_price_range(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '10', 'max_price': '30', 'compare': 'gt', 'count': '3'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data]
        self.assertIn(self.pharmacy2.id, ids)
        self.assertNotIn(self.pharmacy1.id, ids)
        self.assertNotIn(self.pharmacy3.id, ids)

    def test_pharmacies_with_mask_count_lte_3_in_price_range(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '5', 'max_price': '25', 'compare': 'lte', 'count': '3'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data]
        self.assertIn(self.pharmacy1.id, ids)
        self.assertIn(self.pharmacy3.id, ids)
        self.assertNotIn(self.pharmacy2.id, ids)

    def test_no_compare_returns_all_pharmacies(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '0', 'max_price': '100'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data]
        self.assertIn(self.pharmacy1.id, ids)
        self.assertIn(self.pharmacy2.id, ids)
        self.assertIn(self.pharmacy3.id, ids)

    def test_invalid_min_price(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': 'invalid', 'max_price': '30', 'compare': 'gt', 'count': '3'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_max_price(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '10', 'max_price': 'oops', 'compare': 'gte', 'count': '2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_count(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '5', 'max_price': '30', 'compare': 'lt', 'count': 'x'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_compare_operator(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url, {'min_price': '5', 'max_price': '30', 'compare': 'not_valid', 'count': '2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_default_values_used_when_missing(self):
        url = reverse('pharmacies-mask-count-filter')
        response = self.client.get(url)  # No parameters at all
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in response.data]
        self.assertEqual(set(ids), {self.pharmacy1.id, self.pharmacy2.id, self.pharmacy3.id})

class TopUsersByTransactionAmountViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(name="User One", cash_balance=1000)
        self.user2 = User.objects.create(name="User Two", cash_balance=1000)
        self.user3 = User.objects.create(name="User Three", cash_balance=1000)

        self.pharmacy = Pharmacy.objects.create(name="Pharmacy", cash_balance=5000)
        self.mask = Mask.objects.create(pharmacy=self.pharmacy, name="N95", price=50.0)

        # Transaction dates (aware datetimes)
        today_naive = datetime.today()
        today = timezone.make_aware(today_naive)

        self.start_date = today - timedelta(days=30)
        self.end_date = today + timedelta(days=1)

        # Create transactions with aware datetime
        Transaction.objects.create(
            user=self.user1, pharmacy=self.pharmacy, mask=self.mask,
            transaction_amount=200, transaction_date=timezone.make_aware(today_naive - timedelta(days=10))
        )
        Transaction.objects.create(
            user=self.user1, pharmacy=self.pharmacy, mask=self.mask,
            transaction_amount=300, transaction_date=timezone.make_aware(today_naive - timedelta(days=5))
        )
        Transaction.objects.create(
            user=self.user2, pharmacy=self.pharmacy, mask=self.mask,
            transaction_amount=600, transaction_date=timezone.make_aware(today_naive - timedelta(days=3))
        )
        Transaction.objects.create(
            user=self.user3, pharmacy=self.pharmacy, mask=self.mask,
            transaction_amount=100, transaction_date=timezone.make_aware(today_naive - timedelta(days=40))  # Outside range
        )

    def test_top_users_by_transaction_amount_within_range(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'limit': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [user['id'] for user in response.data]
        self.assertEqual(len(result_ids), 2)
        self.assertEqual(result_ids[0], self.user2.id)  # 600
        self.assertEqual(result_ids[1], self.user1.id)  # 500

    def test_excludes_transactions_out_of_range(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'limit': 10
        })
        ids = [user['id'] for user in response.data]
        self.assertNotIn(self.user3.id, ids)

    def test_invalid_start_date_format(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': 'bad-date',
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'limit': 10
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_date", str(response.data).lower())

    def test_invalid_end_date_format(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': 'bad-end',
            'limit': 10
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", str(response.data).lower())

    def test_no_transactions_in_range(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': '2000-01-01',
            'end_date': '2000-01-10',
            'limit': 5
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_limit_applied_correctly(self):
        url = reverse('top-users-by-transaction')
        response = self.client.get(url, {
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'limit': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.user2.id)

class TotalMaskSoldViewTest(APITestCase):
    def setUp(self):
        # Create user and pharmacy
        self.user = User.objects.create(name="Test User", cash_balance=Decimal("1000.00"))
        self.pharmacy = Pharmacy.objects.create(name="Test Pharmacy", cash_balance=Decimal("2000.00"))

        # Create a mask
        self.mask = Mask.objects.create(pharmacy=self.pharmacy, name="Test Mask", price=Decimal("50.00"))

        # today = timezone.now().date()
        today_naive = datetime.today()
        today = timezone.make_aware(today_naive)

        # Transactions within range (3)
        for i in range(3):
            Transaction.objects.create(
                user=self.user,
                pharmacy=self.pharmacy,
                mask=self.mask,
                transaction_amount=Decimal("100.00"),
                transaction_date=today - timedelta(days=i)
            )

        # Transactions outside range (2)
        for i in range(2):
            Transaction.objects.create(
                user=self.user,
                pharmacy=self.pharmacy,
                mask=self.mask,
                transaction_amount=Decimal("200.00"),
                transaction_date=today - timedelta(days=40 + i)
            )

    def test_summary_within_date_range(self):
        start_date = (timezone.now().date() - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = timezone.now().date().strftime('%Y-%m-%d')
        url = reverse('transactions-summary')

        response = self.client.get(url, {'start_date': start_date, 'end_date': end_date})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_masks_sold'], 3)
        self.assertEqual(Decimal(response.data['total_transaction_value']), Decimal("300.00"))

    def test_missing_start_date(self):
        url = reverse('transactions-summary')
        response = self.client.get(url, {'end_date': '2025-01-01'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', str(response.data))

    def test_invalid_date_format(self):
        url = reverse('transactions-summary')
        response = self.client.get(url, {'start_date': '01-01-2025', 'end_date': '2025-01-01'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', str(response.data))

    def test_empty_transactions(self):
        Transaction.objects.all().delete()
        start_date = (timezone.now().date() - timedelta(days=5)).strftime('%Y-%m-%d')
        end_date = timezone.now().date().strftime('%Y-%m-%d')
        url = reverse('transactions-summary')

        response = self.client.get(url, {'start_date': start_date, 'end_date': end_date})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_masks_sold'], 0)
        self.assertEqual(response.data['total_transaction_value'], 0)

    def test_start_date_after_end_date(self):
        url = reverse('transactions-summary')
        response = self.client.get(url, {'start_date': '2025-01-10', 'end_date': '2025-01-01'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_masks_sold'], 0)
        self.assertEqual(response.data['total_transaction_value'], 0)


class SearchViewTests(APITestCase):
    def setUp(self):
        self.pharmacy1 = Pharmacy.objects.create(name="Carepoint", cash_balance=1000)
        self.pharmacy2 = Pharmacy.objects.create(name="DFW Wellness", cash_balance=2000)
        self.mask1 = Mask.objects.create(pharmacy=self.pharmacy1, name="Test Mask", price=Decimal("50.00"))
        self.mask2 = Mask.objects.create(pharmacy=self.pharmacy2, name="test mask2", price=Decimal("100.00"))
        self.url = reverse('search')  # Make sure your URL name is 'search'

    def test_search_without_query_returns_error(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Query parameter is required.", str(response.data))

    def test_search_masks_only(self):
        response = self.client.get(self.url, {'query': 'mask', 'category': 'masks'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('masks', response.data)
        self.assertEqual(len(response.data['masks']), 2)
        self.assertNotIn('pharmacies', response.data)

    def test_search_pharmacies_only(self):
        response = self.client.get(self.url, {'query': 'carepoint', 'category': 'pharmacies'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pharmacies', response.data)
        self.assertEqual(len(response.data['pharmacies']), 1)
        self.assertNotIn('masks', response.data)

    def test_search_all_categories(self):
        response = self.client.get(self.url, {'query': 'carepoint'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('masks', response.data)
        self.assertIn('pharmacies', response.data)

    def test_case_insensitive_search(self):
        response = self.client.get(self.url, {'query': 'TEST MASK2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['masks']), 1)
        self.assertEqual(response.data['masks'][0]['name'], 'test mask2')