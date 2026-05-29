#!/usr/bin/env python
"""B1 검증 하네스 — 표준 Django manage.py."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "b1verify.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
