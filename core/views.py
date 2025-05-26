from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.dateparse import parse_time
from django.utils import timezone
from .utils import parse_date_param
from datetime import datetime
from django.db.models import Count, Sum, Q
from rest_framework.exceptions import ValidationError
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction
from .serializers import UserSerializer, PharmacySerializer, PharmacyOpeningHourSerializer, MaskSerializer, TransactionSerializer

# --- User Views ---
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TopUsersByTransactionAmountView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        params = self.request.query_params
        
        start_date = parse_date_param(params.get('start_date'), 'start_date')
        end_date = parse_date_param(params.get('end_date'), 'end_date')

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

class TotalMaskSoldView(APIView): #within date
    def get(self, request):
        params = request.query_params

        start_date = parse_date_param(params.get('start_date'), 'start_date')
        end_date = parse_date_param(params.get('end_date'), 'end_date')

        summary = (
            Transaction.objects
            .filter(transaction_date__range=(start_date, end_date))
            .aggregate(
                total_masks_sold=Count('id'),
                total_transaction_value=Sum('transaction_amount')
            )
        )

        # If no transactions found, defaults to None, replace with 0
        summary['total_masks_sold'] = summary['total_masks_sold'] or 0
        summary['total_transaction_value'] = summary['total_transaction_value'] or 0

        return Response(summary)

class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        category = request.query_params.get('category')  # Optional: "masks" or "pharmacies"

        if not query:
            raise ValidationError("Query parameter is required.")

        results = {}

        if not category or category == 'masks':
            masks = Mask.objects.filter(
                Q(name__icontains=query) | Q(name__istartswith=query)
            ).annotate(
                relevance=Count('id')  # Optional: sort logic placeholder
            ).order_by('-relevance')
            results['masks'] = MaskSerializer(masks, many=True).data

        if not category or category == 'pharmacies':
            pharmacies = Pharmacy.objects.filter(
                Q(name__icontains=query) | Q(name__istartswith=query)
            ).annotate(
                relevance=Count('id')  # Optional: sort logic placeholder
            ).order_by('-relevance')
            results['pharmacies'] = PharmacySerializer(pharmacies, many=True).data

        return Response(results)

# TODO: Task 7
# Create a view to handle the process of a user purchasing masks,
# possibly from different pharmacies.
# - URL: /api/purchase/
# - Method: POST
# - Body: { user_id, purchases: [{pharmacy_id, mask_id, quantity}, ...] }
# - Update balances, create Transaction, reduce stock (if modeled)
