from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('loan/apply/', views.loan_apply_view, name='loan_apply'),
    path('loan/<int:pk>/', views.loan_detail_view, name='loan_detail'),
    path('my-loans/', views.my_loans_view, name='my_loans'),
    path('profile/', views.profile_view, name='profile'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('transactions/', views.transactions_view, name='transactions'),
]
