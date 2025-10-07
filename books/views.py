from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Book, BookRequest, Category
from .forms import BookForm, BookRequestForm
from transactions.models import Transaction

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/list.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        return Book.objects.filter(available_copies__gt=0)

class BookSearchView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/search.html'
    context_object_name = 'books'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
        return Book.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_type == 'student':
            existing_request = BookRequest.objects.filter(
                student=self.request.user,
                book=self.object,
                status__in=['pending', 'approved']
            ).first()
            context['existing_request'] = existing_request
        return context

class AddBookView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/add.html'
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        form.instance.available_copies = form.instance.total_copies
        messages.success(self.request, 'Book added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.get_absolute_url()

class RequestBookView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        return self.request.user.user_type == 'student'
    
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Check if student already has a pending or approved request for this book
        existing_request = BookRequest.objects.filter(
            student=request.user,
            book=book,
            status__in=['pending', 'approved']
        ).first()
        
        if existing_request:
            messages.error(request, 'You already have a request for this book.')
        elif not book.is_available:
            messages.error(request, 'This book is not available.')
        else:
            BookRequest.objects.create(
                student=request.user,
                book=book
            )
            messages.success(request, 'Book request submitted successfully!')
        
        return redirect('books:detail', pk=pk)

class BookRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BookRequest
    template_name = 'books/requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def get_queryset(self):
        return BookRequest.objects.filter(status='pending')

class MyRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BookRequest
    template_name = 'books/my_requests.html'
    context_object_name = 'requests'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.user_type == 'student'
    
    def get_queryset(self):
        return BookRequest.objects.filter(student=self.request.user)

class ApproveRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def post(self, request, pk):
        book_request = get_object_or_404(BookRequest, pk=pk)
        
        if book_request.book.available_copies > 0:
            book_request.status = 'approved'
            book_request.approved_by = request.user
            book_request.approval_date = timezone.now()
            book_request.due_date = timezone.now() + timedelta(days=14)  # 2 weeks
            book_request.save()
            
            # Decrease available copies
            book_request.book.available_copies -= 1
            book_request.book.save()
            
            # Create transaction
            Transaction.objects.create(
                student=book_request.student,
                book=book_request.book,
                transaction_type='issue',
                due_date=book_request.due_date,
                processed_by=request.user
            )
            
            messages.success(request, 'Book request approved successfully!')
        else:
            messages.error(request, 'Book is not available.')
        
        return redirect('books:requests')

class RejectRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        return self.request.user.user_type == 'admin'
    
    def post(self, request, pk):
        book_request = get_object_or_404(BookRequest, pk=pk)
        book_request.status = 'rejected'
        book_request.approved_by = request.user
        book_request.approval_date = timezone.now()
        book_request.save()
        
        messages.success(request, 'Book request rejected.')
        return redirect('books:requests')

class ReturnBookView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        return self.request.user.user_type == 'student'
    
    def post(self, request, pk):
        book_request = get_object_or_404(BookRequest, pk=pk, student=request.user, status='approved')
        
        book_request.status = 'returned'
        book_request.return_date = timezone.now()
        book_request.save()
        
        # Increase available copies
        book_request.book.available_copies += 1
        book_request.book.save()
        
        # Create return transaction
        Transaction.objects.create(
            student=request.user,
            book=book_request.book,
            transaction_type='return',
            return_date=timezone.now(),
            processed_by=request.user  # Self-return, could be modified for admin processing
        )
        
        messages.success(request, 'Book returned successfully!')
        return redirect('books:my_requests')