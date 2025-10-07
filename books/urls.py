from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('search/', views.BookSearchView.as_view(), name='search'),
    path('add/', views.AddBookView.as_view(), name='add'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('<int:pk>/request/', views.RequestBookView.as_view(), name='request'),
    path('requests/', views.BookRequestListView.as_view(), name='requests'),
    path('requests/<int:pk>/approve/', views.ApproveRequestView.as_view(), name='approve_request'),
    path('requests/<int:pk>/reject/', views.RejectRequestView.as_view(), name='reject_request'),
    path('my-requests/', views.MyRequestsView.as_view(), name='my_requests'),
    path('return/<int:pk>/', views.ReturnBookView.as_view(), name='return'),
]