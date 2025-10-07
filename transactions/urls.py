from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),
    path('my-transactions/', views.MyTransactionsView.as_view(), name='my_transactions'),
    path('fines/', views.FineListView.as_view(), name='fines'),
    path('my-fines/', views.MyFinesView.as_view(), name='my_fines'),
]