from django.contrib import admin
from .models import Category, Book, BookRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'added_by', 'created_at')
    list_filter = ('category', 'added_by', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'category', 'description')
        }),
        ('Publication Details', {
            'fields': ('publisher', 'publication_date', 'pages')
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Media Files', {
            'fields': ('cover_image', 'pdf_file')
        }),
        ('Metadata', {
            'fields': ('added_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'status', 'request_date', 'approved_by', 'approval_date')
    list_filter = ('status', 'request_date', 'approval_date')
    search_fields = ('student__username', 'student__full_name', 'book__title')
    ordering = ('-request_date',)
    readonly_fields = ('request_date',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('student', 'book', 'status', 'notes')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'approval_date', 'due_date')
        }),
        ('Return Information', {
            'fields': ('return_date',)
        }),
        ('Metadata', {
            'fields': ('request_date',),
            'classes': ('collapse',)
        }),
    )