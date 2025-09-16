#!/usr/bin/env python
import os
import sys
from settings.conf import ENV_ID, ENV_POSSIBLE_OPTIONS

def main():
    """Run administrative tasks."""
    assert ENV_ID in ENV_POSSIBLE_OPTIONS, f"Set correct DJANGORLAR_ENV_ID env var. Possible options: {ENV_POSSIBLE_OPTIONS}"
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{ENV_ID}')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
