import datetime

from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from .models import Book, User, BorrowRecord
from .forms import RegistrationForm, BookForm
from .mixins import LibrarianRequiredMixin, ReaderRequiredMixin, LoginRequiredMixin


class HomeView(ListView):
    model = Book
    template_name = 'library/home.html'
    context_object_name = 'books'
    paginate_by = 6  # Keeps the book browsing catalog clean and paginated

    def get_queryset(self):
        queryset = Book.objects.all().order_by('title')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch global catalog statistics for the landing cards
        context['total_issued_copies'] = BorrowRecord.objects.filter(status=BorrowRecord.StatusChoices.BORROWED).count()
        return context


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'library/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # Auto-login after registration
        if user.is_librarian:
            return redirect('librarian_dashboard')
        return redirect('reader_dashboard')


class CustomLoginView(LoginView):
    template_name = 'library/login.html'

    def get_success_url(self):
        if self.request.user.is_librarian:
            return reverse_lazy('librarian_dashboard')
        return reverse_lazy('reader_dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


# Dashboards
class LibrarianDashboardView(LibrarianRequiredMixin, ListView):
    model = Book
    template_name = 'library/librarian_dashboard.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        """Intercepts and filters the base catalog queryset based on URL search query rules."""
        queryset = Book.objects.all()
        query = self.request.GET.get('q')  # Captures the text typed inside the search bar

        if query:
            # Performs a case-insensitive lookup across Title, Author, or ISBN records
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add active active operations list tracking to the admin pane
        context['active_borrowings'] = BorrowRecord.objects.filter(status=BorrowRecord.StatusChoices.BORROWED)
        context['readers'] = User.objects.filter(role=User.Roles.READER).order_by('username')
        return context


class ReaderDashboardView(ReaderRequiredMixin, ListView):
    model = Book
    template_name = 'library/reader_dashboard.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query)
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Display the reader's personal loan book shelf
        context['my_borrowings'] = BorrowRecord.objects.filter(user=self.request.user)
        return context


# Book Operations
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('librarian_dashboard')


class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('librarian_dashboard')


class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('librarian_dashboard')


class IssueBookView(LibrarianRequiredMixin, View):
    """View handling the physical allocation of a book copy to a system reader user."""

    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        username = request.POST.get('username')

        reader = get_object_or_404(User, username=username, role=User.Roles.READER)

        with transaction.atomic():
            book = get_object_or_404(Book.objects.select_for_update(), id=book_id)

            # Scenario handling validation guardrails
            if book.available_copies < 1:
                messages.error(request, f"Operation Denied: '{book.title}' is completely checked out.")
                return redirect('librarian_dashboard')

            if BorrowRecord.objects.filter(user=reader, book=book, status=BorrowRecord.StatusChoices.BORROWED).exists():
                messages.error(request, f"User {username} currently holds an unreturned copy of this volume.")
                return redirect('librarian_dashboard')

            # Decrement inventory and save transaction allocation metrics
            book.available_copies -= 1
            book.save()

            BorrowRecord.objects.create(
                user=reader,
                book=book,
                due_date=timezone.now().date() + datetime.timedelta(days=14)  # 2-Week standard checkout period
            )
            messages.success(request, f"Success: '{book.title}' effectively provisioned out to user {username}.")

        return redirect('librarian_dashboard')


class ReturnBookView(LibrarianRequiredMixin, View):
    """View handling processing returns, updating stock, and settling dynamic system fines."""

    def post(self, request, pk, *args, **kwargs):
        with transaction.atomic():
            record = get_object_or_404(BorrowRecord.objects.select_for_update(), id=pk)

            if record.status == BorrowRecord.StatusChoices.RETURNED:
                messages.warning(request, "This active borrowing execution track has already been settled.")
                return redirect('librarian_dashboard')

            book = record.book
            book.available_copies += 1
            book.save()

            # Close loan metrics tracking window
            record.return_date = timezone.now().date()
            record.status = BorrowRecord.StatusChoices.RETURNED

            # Freeze accumulated dynamic penalties permanently to ledger
            current_fine = record.calculate_fine
            if current_fine > 0:
                record.final_fine_amount = current_fine
                messages.error(request,
                               f"Asset Returned OVERDUE. Penalty Ledger balance generated: ${current_fine:.2f}.")
            else:
                messages.success(request, f"Success: '{book.title}' checked back into inventory cleanly.")

            record.save()

        return redirect('librarian_dashboard')


class CollectFineView(LibrarianRequiredMixin, View):
    """Clears the outstanding fine from a returned historical ledger item entry."""

    def post(self, request, pk, *args, **kwargs):
        record = get_object_or_404(BorrowRecord, id=pk)
        record.fine_paid = True
        record.save()
        messages.success(request, f"Payment Verified: Balance for user {record.user.username} settled cleanly.")
        return redirect('librarian_dashboard')


class DeleteReaderView(LibrarianRequiredMixin, View):
    """Allows librarians to delete reader accounts."""

    def post(self, request, pk, *args, **kwargs):
        reader = get_object_or_404(User, pk=pk, role=User.Roles.READER)

        if BorrowRecord.objects.filter(user=reader, status=BorrowRecord.StatusChoices.BORROWED).exists():
            messages.error(
                request,
                f"Cannot delete {reader.username}. This reader still has active borrowed books."
            )
            return redirect('librarian_dashboard')

        username = reader.username
        reader.delete()
        messages.success(request, f"Reader account '{username}' deleted successfully.")
        return redirect('librarian_dashboard')