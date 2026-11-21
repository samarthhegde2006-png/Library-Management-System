from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('issue/', views.issue_books_view, name='issue_books'),
    path('slip/<str:slip_number>/', views.slip_confirmation, name='slip_confirmation'),
    path('track/', views.track_borrow_view, name='track_borrow'),
    path('return/<str:slip_number>/', views.return_books_view, name='return_books'),
    path('renew/<str:slip_number>/', views.renew_slip_view, name='renew_slip'),
]
