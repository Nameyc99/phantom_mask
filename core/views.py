from rest_framework.generics import ListAPIView
from django.utils.dateparse import parse_time
from .models import User, Pharmacy, PharmacyOpeningHour, Mask, Transaction
from .serializers import UserSerializer, PharmacySerializer, PharmacyOpeningHourSerializer, MaskSerializer, TransactionSerializer

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PharmacyListView(ListAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

class PharmaciesOpenListView(ListAPIView):
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

class PharmacyOpeningHourListView(ListAPIView):
    queryset = PharmacyOpeningHour.objects.all()
    serializer_class = PharmacyOpeningHourSerializer

class MaskListView(ListAPIView):
    queryset = Mask.objects.all()
    serializer_class = MaskSerializer

class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
