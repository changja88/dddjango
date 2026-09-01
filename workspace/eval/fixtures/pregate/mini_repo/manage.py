#!/usr/bin/env python3
"""픽스처 최소 manage.py — `<project>` 판정(manage.py 1순위)의 결정 재료."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
