from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST
from library.models import BookBag, Book
from .models import BorrowSlip, BorrowedBookItem


@login_required
def issue_books_view(request):
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    items = bag.items.select_related('book').all()
    if not items.exists():
        messages.warning(request, 'Your Book Bag is empty.')
        return redirect('library:catalog')

    if request.method == 'POST':
        member_name = request.POST.get('member_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        address = request.POST.get('delivery_address', '').strip()
        mode = request.POST.get('borrow_mode', 'IN_PERSON')
        loan_days = int(request.POST.get('loan_days', 14))
        voucher = request.POST.get('voucher_code', '').strip().upper()

        with transaction.atomic():
            locked = []
            for b_item in items:
                bk = Book.objects.select_for_update().get(pk=b_item.book.pk)
                if bk.available_copies < 1:
                    messages.error(request, f'"{bk.title}" just ran out of available copies.')
                    return redirect('library:bag')
                locked.append((b_item, bk))

            slip = BorrowSlip.objects.create(
                user=request.user,
                member_name=member_name or request.user.username,
                email=email or request.user.email,
                phone_number=phone,
                delivery_address=address,
                borrow_mode=mode,
                loan_days=loan_days,
                voucher_code=voucher,
                status='Checked Out',
            )

            for b_item, bk in locked:
                BorrowedBookItem.objects.create(
                    slip=slip,
                    book=bk,
                    book_title=bk.title,
                    author_name=bk.author,
                    selected_edition=b_item.selected_edition,
                    reading_note=b_item.reading_note,
                )
                bk.available_copies = max(0, bk.available_copies - 1)
                bk.popularity_score += 2
                bk.save()

            bag.items.all().delete()

        messages.success(request, f'Borrow Slip {slip.slip_number} issued!')
        return redirect('circulation:slip_confirmation', slip_number=slip.slip_number)

    return render(request, 'circulation/issue_books.html', {
        'bag': bag,
        'items': items,
    })


@login_required
def slip_confirmation(request, slip_number):
    slip = get_object_or_404(BorrowSlip, slip_number=slip_number, user=request.user)
    return render(request, 'circulation/slip_confirmation.html', {'slip': slip})


def track_borrow_view(request):
    query_slip = request.GET.get('slip_number', '').strip().upper()
    tracked_slip = None
    user_slips = []
    if request.user.is_authenticated:
        user_slips = BorrowSlip.objects.filter(user=request.user).prefetch_related('items').order_by('-issued_at')

    if query_slip:
        if request.user.is_authenticated:
            tracked_slip = BorrowSlip.objects.filter(slip_number__iexact=query_slip, user=request.user).prefetch_related('items').first()
        else:
            tracked_slip = BorrowSlip.objects.filter(slip_number__iexact=query_slip).prefetch_related('items').first()
        if not tracked_slip:
            messages.error(request, f'No borrow slip found for "{query_slip}".')

    stages = ['Reserved', 'Checked Out', 'Reading Period Active', 'Returned']
    stage_idx = 1
    if tracked_slip:
        if tracked_slip.status == 'Reserved':
            stage_idx = 0
        elif tracked_slip.status == 'Checked Out':
            stage_idx = 2
        elif tracked_slip.status == 'Returned':
            stage_idx = 3

    return render(request, 'circulation/track_borrow.html', {
        'query_slip': query_slip,
        'tracked_slip': tracked_slip,
        'user_slips': user_slips,
        'stages': stages,
        'stage_idx': stage_idx,
    })


@login_required
@require_POST
def return_books_view(request, slip_number):
    slip = get_object_or_404(BorrowSlip, slip_number=slip_number, user=request.user)
    if slip.status != 'Returned':
        with transaction.atomic():
            for item in slip.items.select_related('book'):
                item.book.available_copies = min(item.book.total_copies, item.book.available_copies + 1)
                item.book.save()
            slip.status = 'Returned'
            slip.returned_at = timezone.now()
            slip.save()
        messages.success(request, f'Books on {slip.slip_number} returned to library shelves.')
    return redirect('accounts:dashboard')


@login_required
@require_POST
def renew_slip_view(request, slip_number):
    slip = get_object_or_404(BorrowSlip, slip_number=slip_number, user=request.user)
    if slip.status != 'Returned':
        slip.due_date = slip.due_date + timedelta(days=7)
        slip.loan_days += 7
        slip.save()
        messages.success(request, f'Extended due date for {slip.slip_number} by 7 days!')
    return redirect('accounts:dashboard')
