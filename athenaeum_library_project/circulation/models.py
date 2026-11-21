import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from library.models import Book


class BorrowSlip(models.Model):
    STATUS_CHOICES = [
        ('Reserved', 'Reserved'),
        ('Checked Out', 'Checked Out'),
        ('Overdue', 'Overdue'),
        ('Returned', 'Returned'),
    ]

    BORROW_MODE_CHOICES = [
        ('IN_PERSON', 'Reading Room & Desk Pickup (Free)'),
        ('COURIER_DELIVERY', 'Home Library Courier Dispatch'),
    ]

    slip_number = models.CharField(max_length=24, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_slips')
    member_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=25)
    delivery_address = models.TextField(blank=True)
    borrow_mode = models.CharField(max_length=30, choices=BORROW_MODE_CHOICES, default='IN_PERSON')
    loan_days = models.PositiveIntegerField(default=14)
    voucher_code = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Checked Out')
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-issued_at']

    def save(self, *args, **kwargs):
        if not self.slip_number:
            self.slip_number = f"ATH-LIB-{uuid.uuid4().hex[:6].upper()}"
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=self.loan_days)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status not in ['Returned'] and timezone.now() > self.due_date

    def __str__(self):
        return self.slip_number


class BorrowedBookItem(models.Model):
    slip = models.ForeignKey(BorrowSlip, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    book_title = models.CharField(max_length=220)
    author_name = models.CharField(max_length=160)
    selected_edition = models.CharField(max_length=100, default='Hardcover')
    reading_note = models.CharField(max_length=200, blank=True)
