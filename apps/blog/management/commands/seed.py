import random
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.text import slugify
from faker import Faker

from apps.blog.models import Category, Comment, Post, Tag

DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500

SEED_PASSWORD = "TestPassword123!"

CATEGORY_NAMES = [
    "Python", "Django", "DevOps", "Backend",
    "Frontend", "Databases", "Testing", "Security",
]

TAG_NAMES = [
    "python", "django", "api", "rest", "backend", 
    "frontend", "postgresql", "sqlite", "docker", 
    "git", "github", "testing", "pytest","security",
    "authentication", "jwt", "deployment", "linux",
    "tutorial", "beginners", 
]

PUBLISHED_PROBABILITY = 0.7
NO_CATEGORY_PROBABAILITY = 0.1
MAX_POST_TAGS = 5

User = get_user_model()

class Command(BaseCommand):
    help = "Fill the database with fake data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users",
            type=int,
            default=DEFAULT_USERS,
            help="Number of users to create",
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=DEFAULT_POSTS,
            help="Number of posts to create",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=DEFAULT_COMMENTS,
            help="Number of comments to create"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        
        if any(
            count < 0
            for count in(users_count, posts_count, comments_count)
        ):
            raise CommandError("Counts cannot be negative.")
        
        if options["clear"]:
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

            self.stdout.write(
                self.style.SUCCESS("Old test data cleared!")
            )
        
        fake = Faker()
        password_hash = make_password(SEED_PASSWORD)

        used_emails = set(
            User.objects.values_list("email", flat=True)
        )

        users = []

        for _ in range(users_count):
            first_name = fake.first_name()
            last_name = fake.last_name()

            email = fake.unique.email()

            while email in used_emails:
                email = fake.unique.email()

            used_emails.add(email)

            users.append(
                User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password_hash,
                    is_active=fake.boolean(chance_of_getting_true=90),
                    is_staff=fake.boolean(chance_of_getting_true=10),
                )
            )

        User.objects.bulk_create(users)

        existing_categories = set(
            Category.objects.values_list("slug", flat=True)
        )
        new_categories = []

        for name in CATEGORY_NAMES:
            slug = slugify(name)
            if slug not in existing_categories:
                new_categories.append(Category(name=name, slug=slug))
                existing_categories.add(slug)

        Category.objects.bulk_create(new_categories)

        existing_tags = set(
            Tag.objects.values_list("slug", flat=True)
        )
        new_tags = []

        for name in TAG_NAMES:
            slug = slugify(name)
            if slug not in existing_tags:
                new_tags.append(Tag(name=name, slug=slug))
                existing_tags.add(slug)

        Tag.objects.bulk_create(new_tags)

        all_users = list(User.objects.all())
        all_categories = list(Category.objects.all())
        all_tags = list(Tag.objects.all())

        if posts_count > 0 and not all_users:
            raise CommandError("Cannot create posts without users.")
        
        used_slugs = set(
            Post.objects.values_list("slug", flat=True)
        )

        posts = []

        for _ in range(posts_count):
            title = fake.sentence(nb_words=6).rstrip(".")
            base_slug = slugify(title)[:40] or "post"
            slug = base_slug
            suffix = 2

            while slug in used_slugs:
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            used_slugs.add(slug)

            category = None
            if all_categories and random.random() >= NO_CATEGORY_PROBABAILITY:
                category = random.choice(all_categories)

            status = (
                Post.Status.PUBLISHED
                if random.random() < PUBLISHED_PROBABILITY
                else Post.Status.DRAFT
            )

            posts.append(
                Post(
                    author=random.choice(all_users),
                    title=title,
                    slug=slug,
                    body="\n\n".join(fake.paragraphs(nb=3)),
                    category=category,
                    status=status,
                )
            )

        Post.objects.bulk_create(posts)

        for post in posts:
            tag_count = random.randint(
                0, min(MAX_POST_TAGS, len(all_tags))
            )

            post.tags.set(random.sample(all_tags, tag_count))

        published_posts = list(
            Post.objects.filter(status=Post.Status.PUBLISHED)
        )

        if comments_count > 0 and not all_users:
            raise CommandError("Cannot create comments without users.")
        
        if comments_count > 0 and not published_posts:
            raise CommandError("Cannot create comments without published posts.")
        
        comments = []

        for _ in range(comments_count):
            comments.append(
                Comment(
                    post=random.choice(published_posts),
                    author=random.choice(all_users),
                    body=fake.paragraph(nb_sentences=2),
                )
            )
        Comment.objects.bulk_create(comments)



        self.stdout.write(
            f"Categories: {len(new_categories)} created"
        )

        self.stdout.write(
            f"Tags: {len(new_tags)} created"
        )

        self.stdout.write(
            self.style.SUCCESS(f"Posts: {len(posts)} created")
        )

        self.stdout.write(
            self.style.SUCCESS(f"Comments: {len(comments)} created")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Users: {len(users)} created"
            )
        )