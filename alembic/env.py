from sqlalchemy import engine_from_config, pool
from alembic import context

from app.models.product import Product
from app.models.category import Category
from app.core.config import settings
from app.database.session import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with sync driver for migrations
# Use pymysql instead of asyncmy for the migration process
import os

# Load .env file to get DB_PASSWORD and other settings
from dotenv import load_dotenv
load_dotenv()

db_password = os.getenv("DB_PASSWORD", "")
config.set_main_option("sqlalchemy.url", f"mysql+pymysql://root:{db_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()