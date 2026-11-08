import os
import sys

from settings.conf import BLOG_ENV_ID


def main() -> None:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        f"settings.env.{BLOG_ENV_ID}",
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()