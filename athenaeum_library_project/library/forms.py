from django import forms
from .models import BookReview, LibrarianInquiry

class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['rating', 'headline', 'comment']

class LibrarianInquiryForm(forms.ModelForm):
    class Meta:
        model = LibrarianInquiry
        fields = ['full_name', 'email', 'subject', 'message']
