import json
from .models import Genre, Book, BookGalleryImage

IMG_CLASSIC = 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=900&q=85'
IMG_STACK = 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=85'
IMG_OPEN = 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=900&q=85'
IMG_COMIC = 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?auto=format&fit=crop&w=900&q=85'
IMG_MANGA = 'https://images.unsplash.com/photo-1618519764620-2073fe5108b6?auto=format&fit=crop&w=900&q=85'
IMG_SCIFI = 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=900&q=85'
IMG_ARCHIVE = 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=900&q=85'
IMG_TECH = 'https://images.unsplash.com/photo-1589998059171-988d887df646?auto=format&fit=crop&w=900&q=85'
IMG_KIDS = 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=900&q=85'


def make_editions(main_img, alt1, alt2):
    return json.dumps([
        {'name': 'Archival Hardcover', 'hex': '#4A2525', 'img': main_img},
        {'name': 'Terracotta Collector', 'hex': '#B86B43', 'img': alt1},
        {'name': 'Sage Library Binding', 'hex': '#586E5C', 'img': alt2},
    ])


def seed_library_catalog():
    if Book.objects.count() >= 18:
        return

    genres_data = [
        ('Classic Literature & Fiction', 'Timeless novels, Pulitzer winners, and literary masterpieces from Dostoevsky, Orwell, Austen, and Márquez.', IMG_CLASSIC, 1),
        ('Comics & Graphic Novels', 'Iconic superhero runs, Vertigo masterpieces, and illustrated graphic literature from DC, Marvel, and Alan Moore.', IMG_COMIC, 2),
        ('Manga & Japanese Sequential Art', 'Critically acclaimed Japanese manga volumes including Berserk, Vagabond, Monster, and One Piece.', IMG_MANGA, 3),
        ('Science, Philosophy & History', 'Landmark works on cosmology, human evolution, Stoic philosophy, and world civilization.', IMG_SCIFI, 4),
        ('Computer Science & Engineering', 'Foundational texts in algorithms, clean software architecture, and artificial intelligence.', IMG_TECH, 5),
        ('Children & Young Readers', 'Beloved illustrated adventures, Harry Potter, The Hobbit, and Percy Jackson for young minds.', IMG_KIDS, 6),
    ]

    genres = {}
    for name, desc, img, order in genres_data:
        g, _ = Genre.objects.get_or_create(name=name, defaults={'description': desc, 'cover_url': img, 'display_order': order})
        genres[name] = g

    books_data = [
        # Real Classic Literature & Fiction
        ('Classic Literature & Fiction', '1984', 'George Orwell', 'Secker & Warburg / Penguin Classics', '978-0451524935', 1949, 328, 'Hardcover', 'Adults', 'Wing A · Shelf 01', 8, True, False, False, IMG_CLASSIC,
         'Winston Smith navigates the totalitarian surveillance state of Oceania under Big Brother in George Orwell’s defining dystopian masterpiece.'),
        ('Classic Literature & Fiction', 'Crime and Punishment', 'Fyodor Dostoevsky', 'Vintage Classics', '978-0679734505', 1866, 671, 'Hardcover', 'Adults', 'Wing A · Shelf 04', 5, True, True, False, IMG_ARCHIVE,
         'Rodion Raskolnikov’s psychological descent through 19th-century St. Petersburg—an enduring meditation on guilt, conscience, and redemption.'),
        ('Classic Literature & Fiction', 'One Hundred Years of Solitude', 'Gabriel García Márquez', 'Harper Perennial', '978-0060883287', 1967, 417, 'Paperback', 'Adults', 'Wing A · Shelf 07', 6, False, False, False, IMG_STACK,
         'The multi-generational chronicle of the Buendía family in the mythical town of Macondo—the pinnacle of magical realism.'),
        ('Classic Literature & Fiction', 'Dune', 'Frank Herbert', 'Ace Books / Chilton', '978-0441172719', 1965, 688, 'Hardcover', 'Young Adult', 'Wing B · Shelf 02', 7, True, False, False, IMG_OPEN,
         'Set on the desert planet Arrakis, Paul Atreides confronts interstellar politics, ecology, and destiny in the greatest science-fiction epic ever written.'),

        # Real Comics & Graphic Novels
        ('Comics & Graphic Novels', 'Watchmen (Deluxe Hardcover)', 'Alan Moore & Dave Gibbons', 'DC Comics / Vertigo', '978-1401245252', 1986, 448, 'Comic / Graphic Novel', 'Adults', 'Graphic Wing · C01', 6, True, True, True, IMG_COMIC,
         'The Hugo Award-winning deconstruction of superhero mythology set in an alternate Cold War 1985.'),
        ('Comics & Graphic Novels', 'Batman: The Dark Knight Returns', 'Frank Miller & Klaus Janson', 'DC Comics', '978-1563893421', 1986, 224, 'Comic / Graphic Novel', 'Young Adult', 'Graphic Wing · C03', 5, True, False, True, IMG_COMIC,
         'Ten years after Bruce Wayne retired the cape, a 55-year-old Batman returns to reclaim Gotham City from the Mutant gang.'),
        ('Comics & Graphic Novels', 'The Sandman Vol. 1: Preludes & Nocturnes', 'Neil Gaiman & Sam Kieth', 'DC Vertigo', '978-1401284770', 1989, 240, 'Comic / Graphic Novel', 'Adults', 'Graphic Wing · C05', 4, False, True, True, IMG_ARCHIVE,
         'Morpheus, the Lord of Dreams, escapes 70 years of occult imprisonment and journeys across realms to reclaim his lost talismans.'),
        ('Comics & Graphic Novels', 'Spider-Man: Kraven’s Last Hunt', 'J.M. DeMatteis & Mike Zeck', 'Marvel Comics', '978-0785134503', 1987, 168, 'Comic / Graphic Novel', 'All Ages', 'Graphic Wing · C08', 7, False, False, True, IMG_COMIC,
         'Sergei Kravinoff buries Spider-Man alive and dons the black suit to prove himself superior to his greatest rival.'),
        ('Comics & Graphic Novels', 'Maus: A Survivor’s Tale (Complete)', 'Art Spiegelman', 'Pantheon Books', '978-0679406419', 1991, 296, 'Comic / Graphic Novel', 'Adults', 'Graphic Wing · C11', 5, True, True, True, IMG_STACK,
         'The Pulitzer Prize-winning graphic memoir depicting Vladek Spiegelman’s survival through the Holocaust.'),

        # Real Manga Volumes
        ('Manga & Japanese Sequential Art', 'Berserk Deluxe Edition Vol. 1', 'Kentaro Miura', 'Dark Horse Manga', '978-1506711980', 1989, 696, 'Manga Volume', 'Adults', 'Manga Vault · M01', 4, True, True, True, IMG_MANGA,
         'Guts, the Black Swordsman, battles demonic apostles across a dark medieval world in Kentaro Miura’s monumental dark-fantasy opus.'),
        ('Manga & Japanese Sequential Art', 'Vagabond (VIZBIG Edition) Vol. 1', 'Takehiko Inoue', 'VIZ Media', '978-1421520544', 1998, 728, 'Manga Volume', 'Adults', 'Manga Vault · M03', 5, True, False, True, IMG_MANGA,
         'Based on Eiji Yoshikawa’s novel Musashi, following Shinmen Takezō’s spiritual path toward becoming invincible under the heavens.'),
        ('Manga & Japanese Sequential Art', 'Monster: The Perfect Edition Vol. 1', 'Naoki Urasawa', 'VIZ Signature', '978-1421569062', 1994, 424, 'Manga Volume', 'Adults', 'Manga Vault · M06', 6, False, False, True, IMG_OPEN,
         'Dr. Kenzo Tenma risks his neurosurgical career in Düsseldorf to save a young boy—only to discover nine years later the child has grown into a charismatic sociopath.'),

        # Science, Philosophy & History
        ('Science, Philosophy & History', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'Harper', '978-0062316097', 2014, 464, 'Hardcover', 'All Ages', 'Wing C · Shelf 01', 9, True, False, False, IMG_SCIFI,
         'How Homo sapiens rose from an insignificant ape to become the master of planet Earth through cognitive, agricultural, and scientific revolutions.'),
        ('Science, Philosophy & History', 'A Brief History of Time', 'Stephen Hawking', 'Bantam Books', '978-0553380163', 1988, 256, 'Paperback', 'Young Adult', 'Wing C · Shelf 03', 7, False, False, False, IMG_SCIFI,
         'Stephen Hawking’s landmark exploration of black holes, the Big Bang, general relativity, and the arrow of time.'),
        ('Science, Philosophy & History', 'Meditations (Gregory Hays Translation)', 'Marcus Aurelius', 'Modern Library', '978-0812968255', 180, 254, 'Rare First Edition', 'Adults', 'Rare Vault · R02', 4, True, True, False, IMG_ARCHIVE,
         'The private Stoic journals of Roman Emperor Marcus Aurelius written on campaign—timeless wisdom on resilience and clarity.'),

        # Computer Science & Engineering
        ('Computer Science & Engineering', 'Clean Code: Agile Software Craftsmanship', 'Robert C. Martin', 'Prentice Hall', '978-0132350884', 2008, 464, 'Academic / Reference', 'Adults', 'Tech Wing · T01', 8, True, False, False, IMG_TECH,
         'Essential principles, patterns, and practices for writing readable, maintainable, and resilient production code.'),
        ('Computer Science & Engineering', 'Introduction to Algorithms (CLRS)', 'Cormen, Leiserson, Rivest & Stein', 'MIT Press', '978-0262046305', 2022, 1312, 'Academic / Reference', 'Adults', 'Tech Wing · T04', 5, False, False, False, IMG_TECH,
         'The comprehensive university and industry standard covering graph theory, dynamic programming, and algorithmic complexity.'),

        # Children & Young Readers
        ('Children & Young Readers', 'The Hobbit (Illustrated Edition)', 'J.R.R. Tolkien', 'HarperCollins', '978-0008376055', 1937, 368, 'Hardcover', 'Kids', 'Junior Wing · J01', 10, True, False, False, IMG_KIDS,
         'Bilbo Baggins is swept from Bag End by Gandalf and thirteen dwarves on a quest to reclaim the Lonely Mountain from Smaug.'),
        ('Children & Young Readers', 'Harry Potter and the Philosopher’s Stone', 'J.K. Rowling', 'Bloomsbury', '978-1408855652', 1997, 352, 'Hardcover', 'Kids', 'Junior Wing · J02', 12, True, False, False, IMG_KIDS,
         'Eleven-year-old Harry Potter discovers his magical heritage and boards the Hogwarts Express for his first year of wizardry.'),
        ('Children & Young Readers', 'Percy Jackson & The Lightning Thief', 'Rick Riordan', 'Disney Hyperion', '978-0786838653', 2005, 377, 'Paperback', 'Kids', 'Junior Wing · J05', 9, False, False, False, IMG_STACK,
         'Percy Jackson discovers he is a demigod son of Poseidon and embarks on a cross-country quest to prevent a war among the Olympian gods.'),
    ]

    for idx, item in enumerate(books_data):
        (g_name, title, author, pub, isbn, yr, pages, fmt, aud, shelf,
         copies, feat, rare, comic, cover, syn) = item

        book, created = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                'genre': genres[g_name],
                'title': title,
                'author': author,
                'publisher': pub,
                'published_year': yr,
                'pages': pages,
                'item_format': fmt,
                'audience': aud,
                'shelf_location': shelf,
                'total_copies': copies,
                'available_copies': copies,
                'synopsis': syn,
                'cover_image_url': cover,
                'edition_variants_json': make_editions(cover, IMG_STACK, IMG_OPEN),
                'is_featured': feat,
                'is_rare_vault': rare,
                'is_comic_or_manga': comic,
                'popularity_score': 100 - idx,
            }
        )
        if created:
            BookGalleryImage.objects.create(book=book, image_url=cover, caption=f'{title} — Cover Artwork')
            BookGalleryImage.objects.create(book=book, image_url=IMG_OPEN, caption='Archival Paper & Typography Spread')
            BookGalleryImage.objects.create(book=book, image_url=IMG_STACK, caption='Spine & Stitched Library Binding')
