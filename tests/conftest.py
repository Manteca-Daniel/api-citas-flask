import sys
import os
import pytest
from unittest.mock import MagicMock

# AÑADIR RUTA RAÍZ DEL PROYECTO AL PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from application import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def mock_db(monkeypatch):
    """
    Mock COMPLETO de MongoDB para soportar:
    myclient["Clinica"]["usuarios"] ...
    myclient["Clinica"]["centros"] ...
    etc.
    """

    mock_client = MagicMock()

    # Diccionario de colecciones
    collections = {
        "usuarios": MagicMock(),
        "centros": MagicMock(),
        "citas": MagicMock(),
    }

    # Mocks por defecto para find / insert
    for col in collections.values():
        col.find.return_value = []
        col.find_one.return_value = None
        col.insert_one.return_value = MagicMock(inserted_id="123")

    # Mock de la base de datos Clinica
    mock_db = MagicMock()
    mock_db.__getitem__.side_effect = lambda name: collections[name]

    # Mock del cliente → myclient["Clinica"]
    mock_client.__getitem__.return_value = mock_db

    # Patch REAL
    monkeypatch.setattr("application.myclient", mock_client)

    # Devolver colecciones por si algún test necesita manipularlas
    return collections
