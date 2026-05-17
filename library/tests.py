import datetime
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from library.forms import BookForm, RegistrationForm
from library.mixins import LibrarianRequiredMixin, ReaderRequiredMixin
from library.models import Book, BorrowRecord, User
from library.views import CustomLoginView


pytestmark = pytest.mark.django_db


@pytest.fixture
def reader_user():
    return get_user_model().objects.create_user(
        username="reader",
        email="reader@example.com",
        password="StrongPass123!",
        role=User.Roles.READER,
    )


@pytest.fixture
def librarian_user():
    return get_user_model().objects.create_user(
        username="librarian",
        email="librarian@example.com",
        password="StrongPass123!",
        role=User.Roles.LIBRARIAN,
    )


@pytest.fixture
def book():
    return Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="1234567890123",
        description="A book about writing clean code.",
        published_date=datetime.date(2008, 8, 1),
        total_copies=3,
    )


class TestUserModel:
    def test_reader_role_properties(self, reader_user):
        assert reader_user.is_reader is True
        assert reader_user.is_librarian is False

    def test_librarian_role_properties(self, librarian_user):
        assert librarian_user.is_librarian is True
        assert librarian_user.is_reader is False


class TestBookModel:
    def test_book_string_representation(self, book):
        assert str(book) == "Clean Code by Robert C. Martin"

    def test_available_copies_equal_total_copies_on_create(self):
        created_book = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt",
            isbn="9876543210123",
            published_date=datetime.date(1999, 10, 20),
            total_copies=5,
            available_copies=1,
        )

        assert created_book.available_copies == 5

    def test_book_ordering_is_newest_first(self):
        older_book = Book.objects.create(
            title="Older Book",
            author="Author One",
            isbn="1111111111111",
            published_date=datetime.date(2020, 1, 1),
            total_copies=1,
        )
        newer_book = Book.objects.create(
            title="Newer Book",
            author="Author Two",
            isbn="2222222222222",
            published_date=datetime.date(2021, 1, 1),
            total_copies=1,
        )

        books = list(Book.objects.all())

        assert books[0] == newer_book
        assert books[1] == older_book


class TestBorrowRecordModel:
    def test_borrow_record_string_representation(self, reader_user, book):
        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=14),
        )

        assert str(record) == "reader - Clean Code (BORROWED)"

    def test_calculate_fine_returns_zero_when_not_overdue(self, reader_user, book):
        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=1),
        )

        assert record.calculate_fine == 0.00

    def test_calculate_fine_returns_amount_when_overdue(self, reader_user, book):
        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() - datetime.timedelta(days=3),
        )

        assert record.calculate_fine == 6.00

    def test_calculate_fine_returns_final_fine_for_returned_record(self, reader_user, book):
        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() - datetime.timedelta(days=3),
            status=BorrowRecord.StatusChoices.RETURNED,
            final_fine_amount=Decimal("10.00"),
        )

        assert record.calculate_fine == Decimal("10.00")


class TestRegistrationForm:
    def test_registration_form_valid_for_reader(self):
        form = RegistrationForm(
            data={
                "username": "newreader",
                "email": "newreader@example.com",
                "role": User.Roles.READER,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        assert form.is_valid() is True

    def test_registration_form_requires_role(self):
        form = RegistrationForm(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            }
        )

        assert form.is_valid() is False
        assert "role" in form.errors


class TestBookForm:
    def test_book_form_valid_on_create(self):
        form = BookForm(
            data={
                "title": "Domain-Driven Design",
                "author": "Eric Evans",
                "isbn": "3333333333333",
                "published_date": "2003-08-30",
                "total_copies": 4,
                "description": "DDD book.",
            }
        )

        assert form.is_valid() is True

    def test_book_form_invalid_when_total_copies_less_than_one(self):
        form = BookForm(
            data={
                "title": "Invalid Book",
                "author": "Author",
                "isbn": "4444444444444",
                "published_date": "2020-01-01",
                "total_copies": 0,
                "description": "Invalid copies.",
            }
        )

        assert form.is_valid() is False
        assert "total_copies" in form.errors

    def test_book_form_prevents_reducing_total_copies_below_borrowed_count(
        self,
        book,
        reader_user,
    ):
        book.available_copies = 1
        book.total_copies = 3
        book.save()

        BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=14),
        )

        form = BookForm(
            instance=book,
            data={
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "published_date": book.published_date,
                "total_copies": 1,
                "description": book.description,
            },
        )

        assert form.is_valid() is False
        assert "Cannot reduce total copies below" in str(form.errors)


class TestMixins:
    def test_librarian_required_mixin_allows_librarian(self, librarian_user):
        request = RequestFactory().get("/")
        request.user = librarian_user

        mixin = LibrarianRequiredMixin()
        mixin.request = request

        assert mixin.test_func() is True

    def test_librarian_required_mixin_blocks_reader(self, reader_user):
        request = RequestFactory().get("/")
        request.user = reader_user

        mixin = LibrarianRequiredMixin()
        mixin.request = request

        assert mixin.test_func() is False

    def test_reader_required_mixin_allows_reader(self, reader_user):
        request = RequestFactory().get("/")
        request.user = reader_user

        mixin = ReaderRequiredMixin()
        mixin.request = request

        assert mixin.test_func() is True

    def test_reader_required_mixin_blocks_librarian(self, librarian_user):
        request = RequestFactory().get("/")
        request.user = librarian_user

        mixin = ReaderRequiredMixin()
        mixin.request = request

        assert mixin.test_func() is False


class TestHomeView:
    def test_home_view_loads_successfully(self, client, book):
        response = client.get(reverse("home"))

        assert response.status_code == 200
        assert "books" in response.context
        assert book in response.context["books"]

    def test_home_view_searches_by_title(self, client, book):
        Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            isbn="5555555555555",
            published_date=datetime.date(2019, 1, 1),
            total_copies=1,
        )

        response = client.get(reverse("home"), {"q": "Clean"})

        assert response.status_code == 200
        assert list(response.context["books"]) == [book]

    def test_home_view_adds_total_issued_copies_to_context(self, client, reader_user, book):
        BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=14),
        )

        response = client.get(reverse("home"))

        assert response.status_code == 200
        assert response.context["total_issued_copies"] == 1


class TestAuthViews:
    def test_register_view_creates_reader_and_redirects_to_reader_dashboard(self, client):
        response = client.post(
            reverse("register"),
            data={
                "username": "registeredreader",
                "email": "registeredreader@example.com",
                "role": User.Roles.READER,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("reader_dashboard")
        assert User.objects.filter(username="registeredreader").exists()

    def test_register_view_creates_librarian_and_redirects_to_librarian_dashboard(self, client):
        response = client.post(
            reverse("register"),
            data={
                "username": "registeredlibrarian",
                "email": "registeredlibrarian@example.com",
                "role": User.Roles.LIBRARIAN,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert User.objects.filter(username="registeredlibrarian").exists()

    def test_login_success_url_for_reader(self, reader_user):
        request = RequestFactory().get("/")
        request.user = reader_user

        view = CustomLoginView()
        view.request = request

        assert view.get_success_url() == reverse("reader_dashboard")

    def test_login_success_url_for_librarian(self, librarian_user):
        request = RequestFactory().get("/")
        request.user = librarian_user

        view = CustomLoginView()
        view.request = request

        assert view.get_success_url() == reverse("librarian_dashboard")


class TestDashboardViews:
    def test_reader_dashboard_requires_login(self, client):
        response = client.get(reverse("reader_dashboard"))

        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_librarian_dashboard_requires_login(self, client):
        response = client.get(reverse("librarian_dashboard"))

        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_reader_dashboard_loads_for_reader(self, client, reader_user, book):
        client.force_login(reader_user)

        response = client.get(reverse("reader_dashboard"))

        assert response.status_code == 200
        assert "books" in response.context
        assert "my_borrowings" in response.context

    def test_librarian_dashboard_loads_for_librarian(self, client, librarian_user, book):
        client.force_login(librarian_user)

        response = client.get(reverse("librarian_dashboard"))

        assert response.status_code == 200
        assert "books" in response.context
        assert "active_borrowings" in response.context
        assert "readers" in response.context

    def test_reader_is_redirected_from_librarian_dashboard(self, client, reader_user):
        client.force_login(reader_user)

        response = client.get(reverse("librarian_dashboard"))

        assert response.status_code == 302
        assert response.url == reverse("reader_dashboard")

    def test_librarian_is_redirected_from_reader_dashboard(self, client, librarian_user):
        client.force_login(librarian_user)

        response = client.get(reverse("reader_dashboard"))

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")


class TestBookViews:
    def test_book_detail_requires_login(self, client, book):
        response = client.get(reverse("book_detail", kwargs={"pk": book.pk}))

        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_book_detail_loads_for_authenticated_user(self, client, reader_user, book):
        client.force_login(reader_user)

        response = client.get(reverse("book_detail", kwargs={"pk": book.pk}))

        assert response.status_code == 200
        assert response.context["book"] == book

    def test_librarian_can_create_book(self, client, librarian_user):
        client.force_login(librarian_user)

        response = client.post(
            reverse("book_create"),
            data={
                "title": "Refactoring",
                "author": "Martin Fowler",
                "isbn": "6666666666666",
                "published_date": "1999-07-08",
                "total_copies": 2,
                "description": "Refactoring book.",
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert Book.objects.filter(title="Refactoring").exists()

    def test_reader_cannot_create_book(self, client, reader_user):
        client.force_login(reader_user)

        response = client.get(reverse("book_create"))

        assert response.status_code == 302
        assert response.url == reverse("reader_dashboard")

    def test_librarian_can_update_book(self, client, librarian_user, book):
        client.force_login(librarian_user)

        response = client.post(
            reverse("book_edit", kwargs={"pk": book.pk}),
            data={
                "title": "Clean Code Updated",
                "author": book.author,
                "isbn": book.isbn,
                "published_date": book.published_date,
                "total_copies": book.total_copies,
                "description": book.description,
            },
        )

        book.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert book.title == "Clean Code Updated"

    def test_librarian_can_delete_book(self, client, librarian_user, book):
        client.force_login(librarian_user)

        response = client.post(reverse("book_delete", kwargs={"pk": book.pk}))

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert Book.objects.filter(pk=book.pk).exists() is False


class TestBorrowingViews:
    def test_librarian_can_issue_book_to_reader(self, client, librarian_user, reader_user, book):
        client.force_login(librarian_user)

        response = client.post(
            reverse("issue_book"),
            data={
                "book_id": book.id,
                "username": reader_user.username,
            },
        )

        book.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert book.available_copies == 2
        assert BorrowRecord.objects.filter(
            user=reader_user,
            book=book,
            status=BorrowRecord.StatusChoices.BORROWED,
        ).exists()

    def test_issue_book_fails_when_no_available_copies(
        self,
        client,
        librarian_user,
        reader_user,
        book,
    ):
        client.force_login(librarian_user)
        book.available_copies = 0
        book.save()

        response = client.post(
            reverse("issue_book"),
            data={
                "book_id": book.id,
                "username": reader_user.username,
            },
        )

        book.refresh_from_db()

        messages = [message.message for message in get_messages(response.wsgi_request)]

        assert response.status_code == 302
        assert book.available_copies == 0
        assert BorrowRecord.objects.count() == 0
        assert any("completely checked out" in message for message in messages)

    def test_issue_book_fails_when_reader_already_borrowed_same_book(
        self,
        client,
        librarian_user,
        reader_user,
        book,
    ):
        client.force_login(librarian_user)

        BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=14),
        )

        response = client.post(
            reverse("issue_book"),
            data={
                "book_id": book.id,
                "username": reader_user.username,
            },
        )

        book.refresh_from_db()

        messages = [message.message for message in get_messages(response.wsgi_request)]

        assert response.status_code == 302
        assert BorrowRecord.objects.count() == 1
        assert book.available_copies == 3
        assert any("currently holds an unreturned copy" in message for message in messages)

    def test_librarian_can_return_book(self, client, librarian_user, reader_user, book):
        client.force_login(librarian_user)

        book.available_copies = 2
        book.save()

        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() + datetime.timedelta(days=14),
        )

        response = client.post(reverse("return_book", kwargs={"pk": record.pk}))

        book.refresh_from_db()
        record.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert book.available_copies == 3
        assert record.status == BorrowRecord.StatusChoices.RETURNED
        assert record.return_date == timezone.now().date()
        assert record.final_fine_amount == 0

    def test_return_already_returned_book_does_not_increment_inventory_again(
        self,
        client,
        librarian_user,
        reader_user,
        book,
    ):
        client.force_login(librarian_user)

        original_available_copies = book.available_copies

        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date(),
            status=BorrowRecord.StatusChoices.RETURNED,
            return_date=timezone.now().date(),
        )

        response = client.post(reverse("return_book", kwargs={"pk": record.pk}))

        book.refresh_from_db()

        messages = [message.message for message in get_messages(response.wsgi_request)]

        assert response.status_code == 302
        assert book.available_copies == original_available_copies
        assert any("already been settled" in message for message in messages)

    def test_librarian_can_collect_fine(self, client, librarian_user, reader_user, book):
        client.force_login(librarian_user)

        record = BorrowRecord.objects.create(
            user=reader_user,
            book=book,
            due_date=timezone.now().date() - datetime.timedelta(days=2),
            status=BorrowRecord.StatusChoices.RETURNED,
            final_fine_amount=Decimal("4.00"),
            fine_paid=False,
        )

        response = client.post(reverse("collect_fine", kwargs={"pk": record.pk}))

        record.refresh_from_db()

        assert response.status_code == 302
        assert response.url == reverse("librarian_dashboard")
        assert record.fine_paid is True

    def test_reader_cannot_issue_book(self, client, reader_user, book):
        client.force_login(reader_user)

        response = client.post(
            reverse("issue_book"),
            data={
                "book_id": book.id,
                "username": reader_user.username,
            },
        )

        assert response.status_code == 302
        assert response.url == reverse("reader_dashboard")