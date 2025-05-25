from django.urls import path
from .views import UserListView, PharmacyListView, PharmaciesOpenAtTimeView, PharmacyMaskListView, PharmacyOpeningHourListView, MaskListView, TransactionListView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('pharmacies/', PharmacyListView.as_view(), name='pharmacy-list'),
    path('pharmacies/open/', PharmaciesOpenAtTimeView.as_view(), name='pharmacies-open'),
    path('pharmacies/<int:pharmacy_id>/masks/', PharmacyMaskListView.as_view(), name='pharmacy-masks'),
    path('opening-hours/', PharmacyOpeningHourListView.as_view(), name='pharmacy-opening-hour-list'),
    path('masks/', MaskListView.as_view(), name='mask-list'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]
