from django.contrib import admin
from .models import BorrowSlip, BorrowedBookItem
admin.site.register([BorrowSlip, BorrowedBookItem])
