#!/usr/bin/env python
"""CLI do Django; PYTHON_ENV escolhe o módulo de settings (dev/test/prod)."""

import os
import sys


def _settings_module() -> str:
    env = os.getenv("PYTHON_ENV", "dev").lower()
    mapping = {
        "production": "config.settings.prod",
        "prod": "config.settings.prod",
        "test": "config.settings.test",
        "dev": "config.settings.dev",
        "development": "config.settings.dev",
    }
    return mapping.get(env, "config.settings.dev")


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", _settings_module())
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
