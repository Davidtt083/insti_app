"""
Configuracion central de la aplicacion.
Lee variables de entorno (via .env con python-dotenv) para no exponer
datos sensibles directamente en el codigo fuente.
"""

import os
from dotenv import load_dotenv

# Ruta base del proyecto (un nivel arriba de app/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Carga variables desde el archivo .env si existe
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Extensiones de archivo permitidas para las entregas de los estudiantes
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "jpg", "jpeg", "png"}


class Config:
    """Configuracion base compartida por todos los entornos."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-insegura-cambiar")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instituto_biblico.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Carpeta fisica donde se guardan los archivos subidos
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", os.path.join(BASE_DIR, "app", "uploads")
    )

    # Limite de tamano por archivo: 10 MB por defecto
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))

    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS

    # Flask-WTF: proteccion CSRF activa por defecto
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
