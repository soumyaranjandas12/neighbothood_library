# seed_books.py
import os
import django
import random
from datetime import date, timedelta

# Initialize Django environment settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_project.settings')
django.setup()

from library.models import Book, User

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

READER_NAMES = [
    "Aarav Sharma", "Priya Nair", "Rohan Mehta", "Sneha Patel", "Vikram Singh",
    "Ananya Gupta", "Rahul Verma", "Meera Iyer", "Arjun Reddy", "Kavya Menon",
    "Nikhil Joshi", "Divya Rao", "Aditya Kumar", "Pooja Shah", "Karan Malhotra",
    "Isha Das", "Siddharth Jain", "Neha Kapoor", "Manish Pillai", "Tanya Bose"
]


def generate_isbn(index):
    """Generates a pseudo-valid unique 13-digit ISBN string."""
    return f"978013468{index:04d}"


def seed_users():
    """Creates one default librarian and twenty default reader accounts."""
    librarian, created = User.objects.get_or_create(
        username='librarian',
        defaults={
            'email': 'librarian@library.com',
            'role': User.Roles.LIBRARIAN,
            'full_name': 'Default Librarian',
            'date_of_birth': date(1990, 1, 1),
            'address': 'Library Admin Office',
            'contact_no': '9999999999',
            'is_staff': True,
        }
    )

    if created:
        librarian.set_password('librarian123')
        librarian.save()
        print("Created default librarian: username='librarian', password='librarian123'")
    else:
        print("Default librarian already exists.")

    readers_created = 0

    for i in range(1, 21):
        full_name = READER_NAMES[i - 1]
        first_name = full_name.split()[0]
        reader_password = f'{first_name}1234#'

        reader, created = User.objects.get_or_create(
            username=f'reader{i}',
            defaults={
                'email': f'reader{i}@library.com',
                'role': User.Roles.READER,
                'full_name': full_name,
                'date_of_birth': date(1995, 1, 1) + timedelta(days=i * 120),
                'address': f'House No. {i}, Main Street, Neighborhood City',
                'contact_no': f'90000000{i:02d}',
            }
        )

        reader.set_password(reader_password)
        reader.save()

        if created:
            readers_created += 1

    print(f"Created {readers_created} default reader accounts.")
    print("Reader usernames: reader1 to reader20")
    print("Reader passwords are their first name followed by 1234#")
    print("Example: Aarav Sharma -> Aarav1234#")


def seed_database():
    print("Initializing bulk inventory seeding process...")

    seed_users()

    books_to_create = []
    start_date = date(2010, 1, 1)

    for i in range(1, 101):
        isbn = generate_isbn(i)

        if Book.objects.filter(isbn=isbn).exists():
            continue

        title = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        # Add volume or part indicators to ensure variations even if titles duplicate
        if i % 4 == 0:
            title += f" (Vol. {random.randint(1, 3)})"

        author = random.choice(AUTHORS)

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
    print(f"Successfully compiled and committed {len(books_to_create)} unique sample book profiles into the registry.")


if __name__ == '__main__':
    seed_database()