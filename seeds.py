# seed_books.py
import os
import django
import random
from datetime import date, timedelta

# Initialize Django environment settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')
django.setup()

from library.models import Book

# Sample lists to dynamically synthesize realistic book configurations
GENRES = ["Fiction", "Sci-Fi", "History", "Biography", "Technology", "Philosophy", "Mystery", "Business", "Poetry",
          "Psychology"]
ADJECTIVES = ["The Last", "Ancient", "Digital", "Echoes of", "Principles of", "Shadow of", "Mastering", "Secrets of",
              "The Art of", "Journey to"]
NOUNS = ["Time", "Python", "Tomorrow", "Leadership", "The Mind", "Empire", "Data Streams", "Humanity", "Algorithms",
         "Silence"]
AUTHORS = [
    "J. Alan", "Sarah Jenkins", "Dr. Robert Chen", "Emma Watson", "Michael Scott",
    "Elena Rostova", "David Miller", "K. Watanabe", "Amara Diallo", "Carlos Gomez"
]


def generate_isbn(index):
    """Generates a pseudo-valid unique 13-digit ISBN string."""
    return f"978013468{index:04d}"


def seed_database():
    print("Initializing bulk inventory seeding process...")

    books_to_create = []
    start_date = date(2010, 1, 1)

    for i in range(1, 101):
        title = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        # Add volume or part indicators to ensure variations even if titles duplicate
        if i % 4 == 0:
            title += f" (Vol. {random.randint(1, 3)})"

        author = random.choice(AUTHORS)
        isbn = generate_isbn(i)

        # Stagger publication dates over the past 15 years
        published_date = start_date + timedelta(days=random.randint(0, 5000))

        # Distribute book counts realistically (between 2 and 15 copies per book)
        total_copies = random.randint(2, 15)

        description = (
            f"A deep and compelling dive into the world of {random.choice(GENRES).lower()}. "
            f"This highly acclaimed piece by {author} challenges standard frameworks and explores "
            f"fundamental themes highly relevant to modern practitioners and global enthusiasts alike."
        )

        books_to_create.append(
            Book(
                title=title,
                author=author,
                isbn=isbn,
                description=description,
                published_date=published_date,
                total_copies=total_copies,
                available_copies=total_copies  # Synced to match initially
            )
        )

    # Execute atomic single-query database injection
    Book.objects.bulk_create(books_to_create)
    print(f"Successfully compiled and committed 100 unique sample book profiles into the registry.")


if __name__ == '__main__':
    seed_database()