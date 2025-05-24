from django.urls import path
from .views import UserListView, PharmacyListView, PharmacyOpeningHourListView, MaskListView, TransactionListView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('pharmacies/', PharmacyListView.as_view(), name='pharmacy-list'),
    path('opening-hours/', PharmacyOpeningHourListView.as_view(), name='pharmacy-opening-hour-list'),
    path('masks/', MaskListView.as_view(), name='mask-list'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]
