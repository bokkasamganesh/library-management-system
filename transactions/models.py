from django.db import models
from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('issue', 'Issue'),
        ('return', 'Return'),
        ('renew', 'Renew'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, 
                                   related_name='processed_transactions', limit_choices_to={'user_type': 'admin'})
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.book.title} ({self.transaction_type})"
    
    class Meta:
        ordering = ['-transaction_date']

class Fine(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Fine - {self.student.full_name} - ${self.amount}"
    
    class Meta:
        ordering = ['-created_at']