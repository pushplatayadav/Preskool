"""Run database migrations for fees app manually."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "preskool.settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    args = [sys.argv[0], "migrate", "fees"]
    sys.stdout.write(f"Running: {' '.join(args)}\n")
    execute_from_command_line(args)
