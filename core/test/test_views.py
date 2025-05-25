from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import time
from core.models import Pharmacy, PharmacyOpeningHour, Mask

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

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
