from django.urls import path
from .views import (UserListView, TopUsersByTransactionAmountView, PharmacyListView, PharmacyOpenAtTimeView, 
                    PharmacyMaskListView, PharmaciesMaskCountFilterView, PharmacyOpeningHourListView, MaskListView, TransactionListView, TotalMaskSoldView, SearchView)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/top/', TopUsersByTransactionAmountView.as_view(), name='top-users-by-transaction'),
    path('pharmacies/', PharmacyListView.as_view(), name='pharmacy-list'),
    path('pharmacies/open/', PharmacyOpenAtTimeView.as_view(), name='pharmacies-open'),
    path('pharmacies/<int:pharmacy_id>/masks/', PharmacyMaskListView.as_view(), name='pharmacy-masks'),
    path('pharmacies/mask-filter/', PharmaciesMaskCountFilterView.as_view(), name='pharmacies-mask-count-filter'),
    path('opening-hours/', PharmacyOpeningHourListView.as_view(), name='pharmacy-opening-hour-list'),
    path('masks/', MaskListView.as_view(), name='mask-list'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/summary/', TotalMaskSoldView.as_view(), name='transactions-summary'),
    path('search/', SearchView.as_view(), name='search')
]
