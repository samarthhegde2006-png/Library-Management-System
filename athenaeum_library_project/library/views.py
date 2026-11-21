from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.views.decorators.http import require_POST

from .models import Genre, Book, ReadingList, ReadingListItem, BookBag, BookBagItem, BookReview
from circulation.models import BorrowSlip
from .forms import BookReviewForm, LibrarianInquiryForm
from .seed import seed_library_catalog


def home(request):
    seed_library_catalog()
    genres = Genre.objects.all()
    featured_books = Book.objects.filter(is_featured=True, is_comic_or_manga=False)[:4]
    comics_and_manga = Book.objects.filter(is_comic_or_manga=True)[:4]
    kids_books = Book.objects.filter(audience='Kids')[:4]
    tech_and_science = Book.objects.filter(genre__slug__in=['science-philosophy-history', 'computer-science-engineering'])[:4]

    return render(request, 'home.html', {
        'genres': genres,
        'featured_books': featured_books,
        'comics_and_manga': comics_and_manga,
        'kids_books': kids_books,
        'tech_and_science': tech_and_science,
    })


def catalog(request):
    seed_library_catalog()
    books = Book.objects.select_related('genre').all()

    q = request.GET.get('q', '').strip()
    genre_slug = request.GET.get('genre', '').strip()
    fmt = request.GET.get('format', '').strip()
    audience = request.GET.get('audience', '').strip()
    avail_only = request.GET.get('available', '').strip()
    sort = request.GET.get('sort', 'popular').strip()

    if genre_slug and genre_slug != 'all':
        books = books.filter(genre__slug=genre_slug)
    if fmt and fmt != 'all':
        books = books.filter(item_format__iexact=fmt)
    if audience and audience != 'all':
        books = books.filter(audience__iexact=audience)
    if avail_only == '1':
        books = books.filter(available_copies__gt=0)
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q) | Q(synopsis__icontains=q))

    if sort == 'newest':
        books = books.order_by('-published_year', '-created_at')
    elif sort == 'title':
        books = books.order_by('title')
    else:
        books = books.order_by('-popularity_score', 'title')

    paginator = Paginator(books, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'genres': Genre.objects.all(),
        'format_choices': Book.FORMAT_CHOICES,
        'audience_choices': Book.AUDIENCE_CHOICES,
        'filters': {
            'q': q, 'genre': genre_slug or 'all', 'format': fmt,
            'audience': audience, 'available': avail_only, 'sort': sort,
        },
    })


def book_detail(request, slug):
    seed_library_catalog()
    book = get_object_or_404(Book.objects.select_related('genre'), slug=slug)
    reviews = book.reviews.select_related('user').all()
    related_books = Book.objects.filter(Q(genre=book.genre) | Q(author=book.author)).exclude(id=book.id)[:4]

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please sign in to post a reader review.')
            return redirect('accounts:login')
        form = BookReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.book = book
            rev.user = request.user
            rev.save()
            messages.success(request, 'Your reader review has been added to the catalog.')
            return redirect('library:book_detail', slug=book.slug)
    else:
        form = BookReviewForm()

    return render(request, 'book_detail.html', {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
        'review_form': form,
    })


# RARE ARCHIVES & COLLECTOR READING ROOM (Unlocked after Sign In)
@login_required
def rare_archives(request):
    seed_library_catalog()
    rare_books = Book.objects.filter(is_rare_vault=True)
    comics_deluxe = Book.objects.filter(is_comic_or_manga=True)
    all_books = Book.objects.all().order_by('title')
    return render(request, 'rare_archives.html', {
        'rare_books': rare_books,
        'comics_deluxe': comics_deluxe,
        'all_books': all_books,
    })


@login_required
@require_POST
def reserve_custom_bundle(request):
    seed_library_catalog()
    book_id = request.POST.get('book_id')
    book = Book.objects.filter(id=book_id).first() or Book.objects.first()
    binding_theme = request.POST.get('binding_theme', 'Burgundy Archival Leather')
    study_room = request.POST.get('study_room', 'Silent Reading Room · Desk 04')
    note = request.POST.get('reading_note', '').strip()

    spec = f"Binding: {binding_theme} | Study Desk: {study_room}" + (f" | Note: {note}" if note else "")
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    BookBagItem.objects.update_or_create(
        bag=bag, book=book,
        defaults={'selected_edition': f"Archival Vault ({binding_theme})", 'reading_note': spec}
    )
    messages.success(request, f'Reserved "{book.title}" with {binding_theme} in your Book Bag!')
    return redirect('library:bag')


def about(request):
    return render(request, 'about.html')


def help_desk(request):
    if request.method == 'POST':
        form = LibrarianInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your inquiry has been logged with the Head Librarian Desk.')
            return redirect('library:help_desk')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': getattr(request.user.member_profile, 'full_name', request.user.username),
                'email': request.user.email,
            }
        form = LibrarianInquiryForm(initial=initial)
    return render(request, 'help_desk.html', {'form': form})


# BOOK BAG & READING LIST
@login_required
def bag_view(request):
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    items = bag.items.select_related('book', 'book__genre').all()
    return render(request, 'bag.html', {'bag': bag, 'items': items})


@login_required
@require_POST
def add_to_bag(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.available_copies < 1:
        messages.error(request, f'All copies of "{book.title}" are currently checked out.')
        return redirect(request.META.get('HTTP_REFERER', 'library:catalog'))

    edition = request.POST.get('selected_edition', '') or book.item_format
    note = request.POST.get('reading_note', '')
    borrow_now = request.POST.get('borrow_now') == '1'

    bag, _ = BookBag.objects.get_or_create(user=request.user)
    BookBagItem.objects.update_or_create(
        bag=bag, book=book,
        defaults={'selected_edition': edition, 'reading_note': note}
    )

    if borrow_now:
        return redirect('circulation:issue_books')

    messages.success(request, f'Added "{book.title}" to your Book Bag.')
    return redirect(request.META.get('HTTP_REFERER', 'library:bag'))


@login_required
@require_POST
def remove_from_bag(request, item_id):
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    get_object_or_404(BookBagItem, id=item_id, bag=bag).delete()
    messages.info(request, 'Removed book from your Book Bag.')
    return redirect('library:bag')


@login_required
def reading_list_view(request):
    rlist, _ = ReadingList.objects.get_or_create(user=request.user)
    items = rlist.items.select_related('book', 'book__genre').all()
    return render(request, 'reading_list.html', {'items': items})


@login_required
@require_POST
def toggle_reading_list(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    rlist, _ = ReadingList.objects.get_or_create(user=request.user)
    existing = ReadingListItem.objects.filter(reading_list=rlist, book=book).first()
    if existing:
        existing.delete()
        messages.info(request, f'Removed "{book.title}" from Reading List.')
    else:
        ReadingListItem.objects.create(reading_list=rlist, book=book)
        messages.success(request, f'Saved "{book.title}" to your Reading List.')
    return redirect(request.META.get('HTTP_REFERER', 'library:reading_list'))


@login_required
@require_POST
def move_saved_to_bag(request, item_id):
    rlist, _ = ReadingList.objects.get_or_create(user=request.user)
    s_item = get_object_or_404(ReadingListItem, id=item_id, reading_list=rlist)
    book = s_item.book
    if book.available_copies < 1:
        messages.error(request, f'No copies of "{book.title}" available right now.')
        return redirect('library:reading_list')
    bag, _ = BookBag.objects.get_or_create(user=request.user)
    BookBagItem.objects.update_or_create(bag=bag, book=book, defaults={'selected_edition': book.item_format})
    s_item.delete()
    messages.success(request, f'Moved "{book.title}" to your Book Bag.')
    return redirect('library:bag')


# LIBRARIAN ADMIN CONSOLE
def is_librarian(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_librarian)
def librarian_console(request):
    seed_library_catalog()
    books = Book.objects.select_related('genre').all().order_by('-created_at')
    slips = BorrowSlip.objects.select_related('user').prefetch_related('items').all().order_by('-issued_at')
    members = User.objects.select_related('member_profile').all().order_by('-date_joined')
    genres = Genre.objects.all()
    total_copies = books.aggregate(total=Sum('total_copies'))['total'] or 0
    available_copies = books.aggregate(avail=Sum('available_copies'))['avail'] or 0

    return render(request, 'librarian_console.html', {
        'books': books,
        'slips': slips,
        'members': members,
        'genres': genres,
        'format_choices': Book.FORMAT_CHOICES,
        'audience_choices': Book.AUDIENCE_CHOICES,
        'total_copies': total_copies,
        'available_copies': available_copies,
    })


@login_required
@user_passes_test(is_librarian)
@require_POST
def librarian_save_book(request):
    book_id = request.POST.get('book_id', '').strip()
    genre = get_object_or_404(Genre, id=request.POST.get('genre_id'))
    book = get_object_or_404(Book, id=book_id) if book_id else Book()

    book.genre = genre
    book.title = request.POST.get('title')
    book.author = request.POST.get('author')
    book.publisher = request.POST.get('publisher', 'Athenaeum Press')
    book.isbn = request.POST.get('isbn')
    book.published_year = int(request.POST.get('published_year', 2024))
    book.pages = int(request.POST.get('pages', 300))
    book.item_format = request.POST.get('item_format', 'Hardcover')
    book.audience = request.POST.get('audience', 'All Ages')
    book.shelf_location = request.POST.get('shelf_location', 'Wing A · Shelf 01')
    copies = int(request.POST.get('total_copies', 5))
    book.total_copies = copies
    book.available_copies = copies
    book.cover_image_url = request.POST.get('cover_image_url', '')
    book.synopsis = request.POST.get('synopsis', '')
    book.is_comic_or_manga = request.POST.get('is_comic_or_manga') == '1'
    book.is_rare_vault = request.POST.get('is_rare_vault') == '1'
    if request.FILES.get('cover_image'):
        book.cover_image = request.FILES['cover_image']
    book.save()

    messages.success(request, f'Catalogued "{book.title}" by {book.author}.')
    return redirect('library:librarian_console')


@login_required
@user_passes_test(is_librarian)
@require_POST
def librarian_delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    book.delete()
    messages.info(request, f'Removed "{title}" from library catalog.')
    return redirect('library:librarian_console')


@login_required
@user_passes_test(is_librarian)
@require_POST
def librarian_update_slip_status(request, slip_id):
    slip = get_object_or_404(BorrowSlip, id=slip_id)
    new_status = request.POST.get('status', slip.status)
    if new_status == 'Returned' and slip.status != 'Returned':
        for item in slip.items.select_related('book'):
            item.book.available_copies = min(item.book.total_copies, item.book.available_copies + 1)
            item.book.save()
    slip.status = new_status
    slip.save()
    messages.success(request, f'Slip {slip.slip_number} updated to {slip.status}.')
    return redirect('library:librarian_console')


def not_found(request, exception):
    return render(request, '404.html', status=404)
