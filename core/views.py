from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_time
from django.utils import timezone
from datetime import datetime
from django.db.models import Count, Sum, Q
from rest_framework.exceptions import ValidationError
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction
from .serializers import UserSerializer, PharmacySerializer, PharmacyOpeningHourSerializer, MaskSerializer, TransactionSerializer

# --- User Views ---
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# TODO: Task 4
# Create a view to retrieve the top X users by total transaction amount
# within a date range.
# - URL: /api/users/top/?start_date=2024-01-01&end_date=2024-12-31&limit=10
class TopUsersByTransactionAmountView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        params = self.request.query_params
        
        # Parse and validate date inputs
        try:
            start_date = timezone.make_aware(datetime.strptime(params.get('start_date'), '%Y-%m-%d'))
        except (TypeError, ValueError):
            raise ValidationError("start_date must be provided in YYYY-MM-DD format.")

        try:
            end_date = timezone.make_aware(datetime.strptime(params.get('end_date'), '%Y-%m-%d'))
        except (TypeError, ValueError):
            raise ValidationError("end_date must be provided in YYYY-MM-DD format.")

        try:
            limit = int(params.get('limit', 10))
        except ValueError:
            raise ValidationError("limit must be an integer.")
        
        queryset = (
            User.objects.annotate(
                total_amount=Sum(
                    'transactions__transaction_amount',
                    filter=Q(transactions__transaction_date__range=(start_date, end_date))
                )
            )
            .filter(total_amount__isnull=False)
            .order_by('-total_amount')[:limit]
        )

        return queryset


# ---Pharmacy Views ---
class PharmacyListView(ListAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

class PharmacyOpeningHourListView(ListAPIView):
    queryset = PharmacyOpeningHour.objects.all()
    serializer_class = PharmacyOpeningHourSerializer
class PharmacyOpenAtTimeView(ListAPIView):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        day = self.request.query_params.get('day')
        time_str = self.request.query_params.get('time')

        if day and time_str:
            query_time = parse_time(time_str)
            if not query_time:
                raise ValidationError("Invalid time format. Expected HH:MM")

            open_ids = PharmacyOpeningHour.objects.filter(
                day_of_week=day,
                open_time__lte=query_time,
                close_time__gte=query_time
            ).values_list('pharmacy_id', flat=True)

            return Pharmacy.objects.filter(id__in=open_ids)

        return Pharmacy.objects.all()


class PharmacyMaskListView(ListAPIView):
    serializer_class = MaskSerializer

    def get_queryset(self):
        pharmacy_id = self.kwargs['pharmacy_id']
        sort_by = self.request.query_params.get('sort_by')
        allowed_sort_fields = ['name', '-name', 'price', '-price']

        if sort_by and sort_by not in allowed_sort_fields:
            raise ValidationError(f"Invalid sort field: {sort_by}")

        queryset = Mask.objects.filter(pharmacy=pharmacy_id)
        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset


class PharmaciesMaskCountFilterView(ListAPIView):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        params = self.request.query_params

        try:
            min_price = float(params.get('min_price', 0))
        except ValueError:
            raise ValidationError("min_price must be a valid number.")

        max_price_param = params.get('max_price')
        if max_price_param is not None:
            try:
                max_price = float(max_price_param)
            except ValueError:
                raise ValidationError("max_price must be a valid number.")
        else:
            max_price = float('inf')

        try:
            count = int(params.get('count', 0))
        except ValueError:
            raise ValidationError("count must be a valid integer.")

        compare = params.get('compare')
        allowed_comparisons = {
            'gt': 'mask_count__gt',
            'lt': 'mask_count__lt',
            'gte': 'mask_count__gte',
            'lte': 'mask_count__lte'
        }

        if compare and compare not in allowed_comparisons:
            raise ValidationError(f"Invalid compare value: '{compare}'. Must be one of {list(allowed_comparisons.keys())}.")

        price_filter = {'price__gte': min_price}
        if max_price != float('inf'):
            price_filter['price__lte'] = max_price

        mask_counts = (
            Mask.objects
            .filter(**price_filter)
            .values('pharmacy_id')
            .annotate(mask_count=Count('id'))
        )

        if compare:
            condition = {allowed_comparisons[compare]: count}
            matching_ids = mask_counts.filter(**condition).values_list('pharmacy_id', flat=True)
            return Pharmacy.objects.filter(id__in=matching_ids)

        return Pharmacy.objects.all()


# ---Mask Views ---
class MaskListView(ListAPIView):
    queryset = Mask.objects.all()
    serializer_class = MaskSerializer

# ---Transaction Views ---
class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer








# TODO: Task 5
# Create a view to calculate the total number of masks sold
# and total transaction value within a date range.
# - URL: /api/transactions/summary/?start_date=...&end_date=...

# TODO: Task 6
# Create a search API to find pharmacies or masks by name,
# and rank by relevance (e.g. name contains, startswith, etc.)
# - URL: /api/search/?query=maskname

# TODO: Task 7
# Create a view to handle the process of a user purchasing masks,
# possibly from different pharmacies.
# - URL: /api/purchase/
# - Method: POST
# - Body: { user_id, purchases: [{pharmacy_id, mask_id, quantity}, ...] }
# - Update balances, create Transaction, reduce stock (if modeled)
