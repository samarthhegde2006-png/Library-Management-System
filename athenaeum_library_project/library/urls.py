from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('rare-archives/', views.rare_archives, name='rare_archives'),
    path('rare-archives/reserve/', views.reserve_custom_bundle, name='reserve_custom_bundle'),
    path('about/', views.about, name='about'),
    path('help-desk/', views.help_desk, name='help_desk'),

    path('bag/', views.bag_view, name='bag'),
    path('bag/add/<int:book_id>/', views.add_to_bag, name='add_to_bag'),
    path('bag/remove/<int:item_id>/', views.remove_from_bag, name='remove_from_bag'),

    path('reading-list/', views.reading_list_view, name='reading_list'),
    path('reading-list/toggle/<int:book_id>/', views.toggle_reading_list, name='toggle_reading_list'),
    path('reading-list/move/<int:item_id>/', views.move_saved_to_bag, name='move_saved_to_bag'),

    path('librarian-console/', views.librarian_console, name='librarian_console'),
    path('librarian-console/book/save/', views.librarian_save_book, name='librarian_save_book'),
    path('librarian-console/book/delete/<int:book_id>/', views.librarian_delete_book, name='librarian_delete_book'),
    path('librarian-console/slip/<int:slip_id>/', views.librarian_update_slip_status, name='librarian_update_slip_status'),
]
