from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_time
from rest_framework.exceptions import ValidationError
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction
from .serializers import UserSerializer, PharmacySerializer, PharmacyOpeningHourSerializer, MaskSerializer, TransactionSerializer

# --- User Views ---
class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        queryset = Pharmacy.objects.all()
        day = self.request.query_params.get('day')
        time_str = self.request.query_params.get('time')

        if day and time_str:
            query_time = parse_time(time_str)
            if not query_time:
                return Pharmacy.objects.none()  # invalid time format

            # Get pharmacy IDs open at the specified time
            open_pharmacies = PharmacyOpeningHour.objects.filter(
                day_of_week=day,
                open_time__lte=query_time,
                close_time__gte=query_time
            ).values_list('pharmacy_id', flat=True)

            queryset = queryset.filter(id__in=open_pharmacies)

        return queryset

class PharmacyMaskListView(ListAPIView):
    serializer_class = MaskSerializer
    
    def get_queryset(self):
        queryset = Mask.objects.filter(pharmacy = self.kwargs['pharmacy_id'])
        sort_by = self.request.query_params.get('sort_by')

        allowed_sort_fields = ['name', '-name', 'price', '-price']

        if sort_by:
            if sort_by not in allowed_sort_fields:
                raise ValidationError(f"Invalid sort field: {sort_by}")
            queryset = queryset.order_by(sort_by)

        return queryset
    
# TODO: Task 3
# Create a view to list pharmacies with more or fewer than X mask products
# within a specific price range.
# - URL: /api/pharmacies/mask-filter/?min_price=10&max_price=30&count_gt=5

# ---Mask Views ---
class MaskListView(ListAPIView):
    queryset = Mask.objects.all()
    serializer_class = MaskSerializer

# ---Transaction Views ---
class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer






# TODO: Task 4
# Create a view to retrieve the top X users by total transaction amount
# within a date range.
# - URL: /api/users/top/?start_date=2024-01-01&end_date=2024-12-31&limit=10

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
