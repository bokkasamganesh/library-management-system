from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    full_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15, unique=True)
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.user_type == 'student' and not self.student_id:
            # Generate unique student ID
            while True:
                student_id = 'STU' + ''.join(random.choices(string.digits, k=6))
                if not User.objects.filter(student_id=student_id).exists():
                    self.student_id = student_id
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} - {self.full_name}"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default='Library Management')
    
    def __str__(self):
        return f"Admin - {self.user.full_name}"