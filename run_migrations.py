"""Run database migrations manually."""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "preskool.settings")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], "makemigrations", "fees"])
    execute_from_command_line([sys.argv[0], "migrate", "fees"])
