import json
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    FORMAT_CHOICES = [
        ('Hardcover', 'Hardcover Edition'),
        ('Paperback', 'Trade Paperback'),
        ('Comic / Graphic Novel', 'Comic / Graphic Novel'),
        ('Manga Volume', 'Manga Tankōbon'),
        ('Academic / Reference', 'Academic & Technical Monograph'),
        ('Rare First Edition', 'Rare Collector First Edition'),
    ]

    AUDIENCE_CHOICES = [
        ('Adults', 'Adults'),
        ('Young Adult', 'Young Adult'),
        ('Kids', 'Kids'),
        ('All Ages', 'All Ages'),
    ]

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    author = models.CharField(max_length=160)
    publisher = models.CharField(max_length=140, default='Oxford & Penguin Press')
    isbn = models.CharField(max_length=32, unique=True)
    published_year = models.PositiveIntegerField(default=2022)
    pages = models.PositiveIntegerField(default=320)
    language = models.CharField(max_length=50, default='English')
    item_format = models.CharField(max_length=60, choices=FORMAT_CHOICES, default='Hardcover')
    audience = models.CharField(max_length=30, choices=AUDIENCE_CHOICES, default='All Ages')
    shelf_location = models.CharField(max_length=80, default='Wing A · Row 04')

    total_copies = models.PositiveIntegerField(default=5)
    available_copies = models.PositiveIntegerField(default=5)

    synopsis = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    cover_image_url = models.URLField(blank=True)
    edition_variants_json = models.TextField(
        blank=True,
        default='[{"name":"Archival Hardcover","hex":"#4A2525","img":""},{"name":"Collector Slipcase","hex":"#B86B43","img":""},{"name":"Library Binding","hex":"#586E5C","img":""}]'
    )

    is_featured = models.BooleanField(default=False)
    is_rare_vault = models.BooleanField(default=False)
    is_comic_or_manga = models.BooleanField(default=False)
    popularity_score = models.PositiveIntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-popularity_score', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.author}")
            slug = base_slug
            c = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{c}"
                c += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def get_cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url or 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=85'

    @property
    def average_rating(self):
        revs = self.reviews.all()
        if not revs.exists():
            return 4.9
        return round(sum(r.rating for r in revs) / revs.count(), 1)

    @property
    def parsed_editions(self):
        try:
            items = json.loads(self.edition_variants_json)
            for item in items:
                if not item.get('img'):
                    item['img'] = self.get_cover
            return items
        except Exception:
            return [{'name': self.item_format, 'hex': '#4A2525', 'img': self.get_cover}]

    def __str__(self):
        return f"{self.title} by {self.author}"


class BookGalleryImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='gallery_images')
    image_url = models.URLField()
    caption = models.CharField(max_length=120, default='Interior Page & Binding Detail')


class ReadingList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reading_list')
    updated_at = models.DateTimeField(auto_now=True)


class ReadingListItem(models.Model):
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reading_list', 'book')
        ordering = ['-added_at']


class BookBag(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='book_bag')
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_books(self):
        return self.items.count()


class BookBagItem(models.Model):
    bag = models.ForeignKey(BookBag, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    selected_edition = models.CharField(max_length=100, default='Standard Library Copy')
    reading_note = models.CharField(max_length=200, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bag', 'book')


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    headline = models.CharField(max_length=140, default='Unforgettable Read')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class LibrarianInquiry(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
