from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import User, AdminProfile
from .forms import StudentRegistrationForm, AdminLoginForm, UserProfileForm
from books.models import BookRequest
from transactions.models import Transaction

class RegisterView(CreateView):
    model = User
    form_class = StudentRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Registration successful! You can now login with your credentials.')
        return super().form_valid(form)

class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and user.user_type == 'student':
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a student account.')
            return render(request, 'accounts/login.html')

class AdminLoginView(View):
    def get(self, request):
        return render(request, 'accounts/admin_login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user and user.user_type == 'admin':
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid admin credentials.')
            return render(request, 'accounts/admin_login.html')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'student':
            context.update({
                'pending_requests': BookRequest.objects.filter(student=user, status='pending').count(),
                'approved_requests': BookRequest.objects.filter(student=user, status='approved').count(),
                'recent_transactions': Transaction.objects.filter(student=user)[:5],
            })
        elif user.user_type == 'admin':
            context.update({
                'pending_requests': BookRequest.objects.filter(status='pending').count(),
                'total_students': User.objects.filter(user_type='student').count(),
                'recent_requests': BookRequest.objects.filter(status='pending')[:5],
            })
        
        return context

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)