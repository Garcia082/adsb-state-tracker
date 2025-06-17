from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- standard -----------------------------------------------------------
config = context.config          # ← ahora SÍ existe
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
# ------------------------------------------------------------------------

# --- bloque que añade la URL en tiempo de ejecución ---------------------
import os, sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

url = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
)
config.set_main_option("sqlalchemy.url", url)

from app import db        # importa tu app
import app.models
target_metadata = db.metadata     # ← para autogenerate
# ------------------------------------------------------------------------



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
