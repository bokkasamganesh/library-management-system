from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from .models import Transaction, Fine

class TransactionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def get_queryset(self):
        return Transaction.objects.all().order_by('-transaction_date')

class MyTransactionsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Transaction
    template_name = 'transactions/my_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'student'
    
    def get_queryset(self):
        return Transaction.objects.filter(student=self.request.user).order_by('-transaction_date')

class FineListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Fine
    template_name = 'transactions/fines.html'
    context_object_name = 'fines'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def get_queryset(self):
        return Fine.objects.all().order_by('-created_at')

class MyFinesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Fine
    template_name = 'transactions/my_fines.html'
    context_object_name = 'fines'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'student'
    
    def get_queryset(self):
        return Fine.objects.filter(student=self.request.user).order_by('-created_at')