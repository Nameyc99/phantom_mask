from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils.dateparse import parse_time
from django.utils import timezone
from .utils import parse_date_param
from datetime import datetime
from django.db.models import Count, Sum, Q
from django.db import transaction as db_transaction
from rest_framework.exceptions import ValidationError
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction
from .serializers import UserSerializer, PharmacySerializer, PharmacyOpeningHourSerializer, MaskSerializer, TransactionSerializer, PurchaseRequestSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

# --- User Views ---
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Start date for the transaction filter (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=True,
            description='End date for the transaction filter (YYYY-MM-DD)'
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Number of top users to return (default: 10)'
        )
    ],
    responses=UserSerializer(many=True)
)
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

@extend_schema(
    parameters=[
        OpenApiParameter(
            name='day',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Day of the week (e.g., Monday, Tuesday)"
        ),
        OpenApiParameter(
            name='time',
            type=OpenApiTypes.TIME,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Time in HH:MM format to check if the pharmacy is open"
        )
    ],
    responses=PharmacySerializer(many=True)
)
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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='sort_by',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Sort by ['name', '-name', 'price', '-price']"
        )
    ],
    responses=MaskSerializer(many=True)
)
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


@extend_schema(
    parameters=[
        OpenApiParameter(name='min_price', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Minimum mask price'),
        OpenApiParameter(name='max_price', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False, description='Maximum mask price'),
        OpenApiParameter(name='count', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='Threshold mask count'),
        OpenApiParameter(name='compare', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description='Comparison operator: gt, lt, gte, lte'),
    ],
    responses=PharmacySerializer(many=True)
)
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

@extend_schema(
    parameters=[
        OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=True, description='Start date in YYYY-MM-DD'),
        OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY, required=True, description='End date in YYYY-MM-DD'),
    ],
    responses={200: OpenApiTypes.OBJECT}
)
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

@extend_schema(
    parameters=[
        OpenApiParameter('query', OpenApiTypes.STR, OpenApiParameter.QUERY, required=True, description="Search query string"),
        OpenApiParameter('category', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False, description="Filter by category: 'masks' or 'pharmacies'"),
    ],
    responses=OpenApiTypes.OBJECT
)
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

@extend_schema(
    request=PurchaseRequestSerializer,
    responses={201: TransactionSerializer(many=True)},
    description="Create multiple purchase transactions for a user in one atomic operation."
)
class PurchaseView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        purchases = data.get('purchases')

        if not user_id or not purchases:
            raise ValidationError("'user_id' and 'purchases' fields are required.")

        try:
            user = User.objects.select_for_update().get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("User not found.")

        created_transactions = []
        total_cost = 0

        # Start atomic transaction
        with db_transaction.atomic():
            for item in purchases:
                pharmacy_id = item.get('pharmacy_id')
                mask_id = item.get('mask_id')
                quantity = item.get('quantity')

                if not all([pharmacy_id, mask_id, quantity]):
                    raise ValidationError("Each purchase must include 'pharmacy_id', 'mask_id', and 'quantity'.")

                try:
                    mask = Mask.objects.get(id=mask_id, pharmacy_id=pharmacy_id)
                except Mask.DoesNotExist:
                    raise ValidationError(f"Mask {mask_id} not found in pharmacy {pharmacy_id}.")

                total_price = mask.price * quantity
                total_cost += total_price

            if user.cash_balance < total_cost:
                raise ValidationError(f"Insufficient funds. Required: {total_cost}, Available: {user.cash_balance}")

            # Perform transactions
            for item in purchases:
                pharmacy_id = item.get('pharmacy_id')
                mask_id = item.get('mask_id')
                quantity = item.get('quantity')

                mask = Mask.objects.get(id=mask_id, pharmacy_id=pharmacy_id)
                pharmacy = mask.pharmacy
                total_price = mask.price * quantity

                # Transfer funds
                user.cash_balance -= total_price
                pharmacy.cash_balance += total_price
                user.save()
                pharmacy.save()

                # Create transaction entry
                transaction = Transaction.objects.create(
                    user=user,
                    pharmacy=pharmacy,
                    mask=mask,
                    transaction_date=timezone.now(),
                    transaction_amount=total_price
                )
                created_transactions.append(transaction)

        return Response(
            TransactionSerializer(created_transactions, many=True).data,
            status=status.HTTP_201_CREATED
        )
