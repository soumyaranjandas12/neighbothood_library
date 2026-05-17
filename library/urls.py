from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Dashboards
    path('dashboard/librarian/', views.LibrarianDashboardView.as_view(), name='librarian_dashboard'),
    path('dashboard/reader/', views.ReaderDashboardView.as_view(), name='reader_dashboard'),

    # Book Actions
    path('book/new/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_edit'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    #Transaction Actions
    path('borrow/issue/', views.IssueBookView.as_view(), name='issue_book'),
    path('borrow/<int:pk>/return/', views.ReturnBookView.as_view(), name='return_book'),
    path('borrow/<int:pk>/pay-fine/', views.CollectFineView.as_view(), name='collect_fine'),
]