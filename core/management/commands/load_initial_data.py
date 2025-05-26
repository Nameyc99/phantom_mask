import os
import json
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Pharmacy, Mask, User, Transaction, PharmacyOpeningHour

class Command(BaseCommand):
    help = 'ETL json data'

    def handle(self, *args, **options):
        # Define your data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(base_dir, 'data')

        # Load data files
        pharmacy_data = self.load_json_file(os.path.join(data_dir, 'pharmacies.json'))
        user_data = self.load_json_file(os.path.join(data_dir, 'users.json'))

        # Process Pharmacies
        self.stdout.write("Processing pharmacies...")
        self.process_pharmacies(pharmacy_data)

        # Process Users
        self.stdout.write("Processing users...")
        self.process_users(user_data)

        self.stdout.write(self.style.SUCCESS("ETL process complete."))

    def load_json_file(self, filepath):
        """Load JSON data from a file."""
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)

    def process_pharmacies(self, data):
        """
        Creates Pharmacy objects along with related Masks
        and parses/stores PharmacyOpeningHour entries.
        """
        for pharmacy_data in data:
            pharmacy = Pharmacy.objects.create(
                name = pharmacy_data['name'],
                cash_balance = pharmacy_data['cashBalance']
            )
            for mask_data in pharmacy_data['masks']:
                Mask.objects.create(
                    pharmacy = pharmacy,
                    name = mask_data['name'],
                    price = mask_data['price']
                )
        
            self.process_opening_hours(pharmacy, pharmacy_data['openingHours'])

    def process_opening_hours(self, pharmacy, opening_hours_str):
        if not opening_hours_str:
            return

        entries = self.parse_opening_hours(opening_hours_str)
        for entry in entries:
            PharmacyOpeningHour.objects.create(
                pharmacy=pharmacy,
                day_of_week=entry['day_of_week'],
                open_time=entry['open_time'],
                close_time=entry['close_time'],
            )

    def parse_opening_hours(self, opening_hours_str):
        """Parse complex strings like 'Mon - Fri 08:00 - 17:00 / Sat, Sun 08:00 - 12:00'"""
        segments = [seg.strip() for seg in opening_hours_str.split('/')]

        results = []
        for segment in segments:
            match = re.match(r'(.+?)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', segment)
            if not match:
                continue

            days_str = match.group(1).strip()
            open_time = datetime.strptime(match.group(2), '%H:%M').time()
            close_time = datetime.strptime(match.group(3), '%H:%M').time()

            days = self.expand_days(days_str)

            for day in days:
                results.append({
                    'day_of_week': day,
                    'open_time': open_time,
                    'close_time': close_time,
                })

        return results

    def expand_days(self, days_str):
        DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        if '-' in days_str:
            start_day, end_day = [d.strip() for d in days_str.split('-')]
            start_index = DAY_ORDER.index(start_day)
            end_index = DAY_ORDER.index(end_day)
            if start_index <= end_index:
                return DAY_ORDER[start_index:end_index + 1]
            else:
                return DAY_ORDER[start_index:] + DAY_ORDER[:end_index + 1]
        else:
            return [d.strip() for d in days_str.split(',')]


    def process_users(self, data):
        """
        TODO: 
        - Create or update User objects
        - Create Transaction records linking Users and Pharmacies
        """
        for user_data in data:
            user_obj = User.objects.create(
                name = user_data['name'],
                cash_balance = user_data['cashBalance']
            )

            for transaction_data in user_data.get('purchaseHistories', []):
                # Find the Pharmacy by name
                pharmacy_obj = Pharmacy.objects.filter(name=transaction_data['pharmacyName']).first()
                if not pharmacy_obj:
                    self.stdout.write(self.style.WARNING(f"Pharmacy '{transaction_data['pharmacyName']}' not found. Skipping transaction."))
                    continue

                # Find the Mask by pharmacy and mask name
                mask_obj = Mask.objects.filter(pharmacy=pharmacy_obj, name=transaction_data['maskName']).first()
                if not mask_obj:
                    self.stdout.write(self.style.WARNING(f"Mask '{transaction_data['maskName']}' not found in pharmacy '{pharmacy_obj.name}'. Skipping transaction."))
                    continue

                # Parse transaction date if available, else use now
                transaction_date = transaction_data.get('transactionDate')
                if transaction_date:
                    dt_naive = datetime.strptime(transaction_date, '%Y-%m-%d %H:%M:%S')
                    transaction_date = timezone.make_aware(dt_naive)
                else:
                    transaction_date = timezone.now()

                # Create Transaction object
                Transaction.objects.create(
                    user=user_obj,
                    pharmacy=pharmacy_obj,
                    mask=mask_obj,
                    transaction_date=transaction_date,
                    transaction_amount=transaction_data['transactionAmount']
                )