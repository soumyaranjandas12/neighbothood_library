from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

class LibrarianRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures the logged-in user is a Librarian."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_librarian

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('reader_dashboard')
        return super().handle_no_permission()

class ReaderRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Ensures the logged-in user is a Reader."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_reader

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('librarian_dashboard')
        return super().handle_no_permission()