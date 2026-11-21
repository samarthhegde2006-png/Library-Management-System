from .models import BookBag, ReadingList, Genre

def global_library_counts(request):
    bag_count = 0
    saved_count = 0
    saved_book_ids = []
    if request.user.is_authenticated:
        bag, _ = BookBag.objects.get_or_create(user=request.user)
        rlist, _ = ReadingList.objects.get_or_create(user=request.user)
        bag_count = bag.total_books
        saved_book_ids = list(rlist.items.values_list('book_id', flat=True))
        saved_count = len(saved_book_ids)
    return {
        'nav_bag_count': bag_count,
        'nav_saved_count': saved_count,
        'saved_book_ids': saved_book_ids,
        'nav_genres': Genre.objects.all(),
    }
