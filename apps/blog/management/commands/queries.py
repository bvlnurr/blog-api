from collections.abc import Callable
from datetime import date
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import connection
from django.db.models import Model, QuerySet
from django.test.utils import CaptureQueriesContext

from apps.blog.models import Post
from apps.blog.queries import QUERIES

PREVIEW_LIMIT = 5
MUTATING_QUERY_NUMBERS = frozenset(range(40, 45))

SAMPLE_ARGUMENTS: dict[int, dict[str, Any]] = {
    7: {"page": 1},
    8: {"word": "a"},
    9: {"domain": "example.com"},
    11: {"slugs": ["backend", "databases"]},
    12: {"year": 2026, "month": 9},
    13: {"days": 30},
    14: {"start": date(2025, 11, 15), "end": date(2026, 11, 15)},
    15: {"email": "ohammond@example.com"},
    16: {"tag_slug": "pytest"},
    17: {"category_slug": "testing"},
    21: {"first_slug": "backend", "second_slug": "github"},
    22: {"text": "a"},
    34: {"min_posts": 2},
    37: {"text": "a"},
    40: {"name": "Django ORM"},
    41: {"days": 30},
    42: {"category_slug": "backend", "tag_slug": "pytest"},
    43: {"source_slug": "backend", "target_slug": "databases"},
}


def get_samole_arguments(number: int) -> dict[str, Any]:
    """Build sample arguments for a query."""
    arguments = SAMPLE_ARGUMENTS.get(number, {}).copy()

    if number == 4:
        slug = Post.objects.order_by("pk").values_list(
            "slug", flat=True
        ).first()
        arguments["slug"] = slug or "mising-post"

    return arguments

class Command(BaseCommand):
    help = "Run Django ORM queries and display SQL statistics."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--number",
            type=int,
            help="Run a specific query by number",
        )
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Display executed SQL statements",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        number = options["number"]
        show_sql = options["sql"]

        if number is not None:
            if number not in QUERIES:
                raise CommandError("Unknown query number: {numner}")
            numbers = [number]
        else:
            numbers = [
                query_number
                for query_number in sorted(QUERIES)
                if query_number not in MUTATING_QUERY_NUMBERS
            ]

        for query_number in numbers:
            function = QUERIES[query_number]
            arguments = get_samole_arguments(query_number)
            self.run_query(
                query_number,
                function,
                arguments,
                show_sql,
            )

    def run_query(
        self,
        number: int,
        function: Callable[..., Any],
        arguments: dict[str, Any],
        show_sql: bool,
    ) -> None:
        """Run a function and capture its SQL statements."""
        annotation_names: tuple[str, ...] = ()

        with CaptureQueriesContext(connection) as context:
            result = function(**arguments)

            if isinstance(result, QuerySet):
                annotation_names = tuple(
                    result.query.annotations
                )
                result = list(result)

            sql_count = len(context.captured_queries)

            self.stdout.write(
                f"\n#{number} {function.__name__} - "
                f"{sql_count} SQL query"
                f"{'ies' if sql_count != 1 else ''}"
            )

            if show_sql:
                for query in context.captured_queries:
                    self.stdout.write(query["sql"])

            self.display_result(result, annotation_names)

    def display_result(self, result: Any, annotation_names: tuple[str, ...] = ()) -> None:
        """Display a result with a limited preview."""
        if isinstance(result, list):
            for item in result[:PREVIEW_LIMIT]:
                self.stdout.write(f" {self.format_item(item, annotation_names)}")

            self.stdout.write(f" ({len(result)} rows)")
            return
        
        self.stdout.write(f" {self.format_item(result, annotation_names)}")

    @staticmethod
    def format_item(item: Any, annotation_names: tuple[str, ...] = ()) -> str:
        """Format model objects including annoted fields."""
        if not isinstance(item, Model):
            return str(item)

        details = {
            name: getattr(item, name)
            for name in annotation_names
        }

        if details:
            return f"{item} {details}"
        
        return str(item)
    