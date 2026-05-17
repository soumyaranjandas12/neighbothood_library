# library/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Book, BorrowRecord


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Extends the built-in UserAdmin to properly display, search, 
    and manage custom user profiles and role parameters.
    """
    # Columns displayed in the user change list overview table
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')

    # Live dashboard filtration side-panel utilities
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')

    # Search functionality targeting key profile identifiers
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # Ordering criteria on initial model loading
    ordering = ('-date_joined',)

    # Extends the creation/editing forms inside admin to include the custom 'role' field
    fieldsets = UserAdmin.fieldsets + (
        ('System Authorization Mapping', {
            'fields': ('role',),
            'description': 'Assign the functional operational tier role parameter for this profile account.'
        }),
    )

    # Fieldsets configuration for the initial user entry form interface
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('System Authorization Mapping', {
            'fields': ('role',),
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Handles internal library collection records, tracking physical inventory 
    and auditing core structural metrics.
    """
    # Columns displayed in the primary book catalog overview table
    list_display = ('title', 'author', 'isbn', 'available_copies', 'total_copies', 'published_date')

    # Fast filtering controls
    list_filter = ('published_date', 'created_at')

    # Dynamic live lookups across text fields
    search_fields = ('title', 'author', 'isbn')

    # Prevents manual overrides on critical framework system dates
    readonly_fields = ('created_at', 'updated_at', 'available_copies')

    # Logical ordering structure
    ordering = ('-created_at',)

    # Grouping input layouts cleanly for management operations
    fieldsets = (
        ('Core Metadata', {
            'fields': ('title', 'author', 'isbn', 'published_date')
        }),
        ('Asset Synopses', {
            'fields': ('description',)
        }),
        ('Inventory Allocation', {
            'fields': ('total_copies', 'available_copies'),
            'description': 'Current internal balance values. Available capacity updates dynamically.'
        }),
        ('System Metadata Audit Logs', {
            'classes': ('collapse',),  # Collapses the section by default for a cleaner UI
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    """
    Admin control tracking external item loans, return state execution logs,
    and outstanding financial liability allocations.
    """
    # Columns displayed in the primary transactional ledger table interface
    list_display = (
        'id',
        'user',
        'book',
        'issue_date',
        'due_date',
        'return_date',
        'status',
        'get_current_fine',
        'fine_paid'
    )

    # Quick filter shortcuts in the right-side layout panel
    list_filter = ('status', 'fine_paid', 'issue_date', 'due_date')

    # Enables quick lookups across specific relational objects
    search_fields = ('user__username', 'user__email', 'book__title', 'book__isbn')

    # Prevents altering operational fields that rely on views logic
    readonly_fields = ('issue_date', 'final_fine_amount')

    # Default ordering hierarchy (most recent transaction loans at the top)
    ordering = ('-issue_date',)

    # Custom bulk admin panel operations
    actions = ['mark_fines_as_paid']

    @admin.display(description='Accrued Fine ($)')
    def get_current_fine(self, obj):
        """Displays live, real-time unreturned fines directly inside the admin change list."""
        # Call the property function configured in models.py
        fine = obj.calculate_fine
        if fine > 0:
            return f"${fine:.2f}"
        return "$0.00"