from django.contrib import admin
from .models import Genre, Book, BookGalleryImage, ReadingList, ReadingListItem, BookBag, BookBagItem, BookReview, LibrarianInquiry
admin.site.register([Genre, Book, BookGalleryImage, ReadingList, ReadingListItem, BookBag, BookBagItem, BookReview, LibrarianInquiry])
