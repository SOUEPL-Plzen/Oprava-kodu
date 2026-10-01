"""Mapa připojení k MySQL v MAMP. Lze přepsat proměnnými prostředí SKLAD_DB_*."""

import os

DB_CONFIG = {
    "host": os.environ.get("SKLAD_DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("SKLAD_DB_PORT", "3306")),
    "user": os.environ.get("SKLAD_DB_USER", "root"),
    "password": os.environ.get("SKLAD_DB_PASSWORD", "root"),
    "database": os.environ.get("SKLAD_DB_NAME", "skladova_karta"),
}
