from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class User(AbstractUser):
    class Roles(models.TextChoices):
        LIBRARIAN = 'LIBRARIAN', 'Librarian'
        READER = 'READER', 'Reader'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.READER
    )
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    contact_no = models.CharField(max_length=20, blank=True)

    @property
    def is_librarian(self):
        return self.role == self.Roles.LIBRARIAN

    @property
    def is_reader(self):
        return self.role == self.Roles.READER


class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    description = models.TextField(blank=True)
    published_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def save(self, *args, **kwargs):
        # On creation, ensure available copies equal total copies
        if not self.pk:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)


class BorrowRecord(models.Model):
    class StatusChoices(models.TextChoices):
        BORROWED = 'BORROWED', 'Borrowed'
        RETURNED = 'RETURNED', 'Returned'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.BORROWED)
    fine_paid = models.BooleanField(default=False)
    final_fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

    @property
    def calculate_fine(self):
        """Dynamically tracks outstanding fine structures prior to closing transaction."""
        FINE_RATE_PER_DAY = 2.00  # Configure your local rate currency standard

        if self.status == self.StatusChoices.RETURNED:
            return self.final_fine_amount

        current_date = timezone.now().date()
        if current_date > self.due_date:
            overdue_days = (current_date - self.due_date).days
            return overdue_days * FINE_RATE_PER_DAY
        return 0.00