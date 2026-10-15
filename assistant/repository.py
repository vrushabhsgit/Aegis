"""Database access layer (implementation to follow)."""


def check_connection() -> bool:
    """Return whether the configured database is reachable."""
    # Keep the initial app runnable before PostgreSQL is configured.
    return False
