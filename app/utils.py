"""
Utilidades compartidas: manejo seguro de archivos y versiculo del dia.
"""

import os
import uuid
from datetime import date

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage, subfolder="submissions"):
    """
    Guarda un archivo subido de forma segura dentro de UPLOAD_FOLDER/subfolder.
    Devuelve (ruta_relativa, extension) o (None, None) si no es valido.
    """
    if not file_storage or file_storage.filename == "":
        return None, None

    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        return None, None

    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    target_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(target_dir, exist_ok=True)

    full_path = os.path.join(target_dir, unique_name)
    file_storage.save(full_path)

    relative_path = os.path.join(subfolder, unique_name)
    return relative_path, ext


# Banco corto de versiculos para el banner devocional del dashboard.
VERSES = [
    ("Josue 1:9", "Esfuerzate y se valiente; no temas ni desmayes, porque el Senor tu Dios estara contigo."),
    ("Proverbios 3:5-6", "Fiate de Jehova de todo tu corazon, y no te apoyes en tu propia prudencia."),
    ("Filipenses 4:13", "Todo lo puedo en Cristo que me fortalece."),
    ("Salmos 119:105", "Lampara es a mis pies tu palabra, y lumbrera a mi camino."),
    ("2 Timoteo 3:16", "Toda la Escritura es inspirada por Dios, y util para ensenar."),
    ("Isaias 41:10", "No temas, porque yo estoy contigo; no desmayes, porque yo soy tu Dios."),
    ("Romanos 12:2", "No os conformeis a este siglo, sino transformaos por la renovacion de vuestro entendimiento."),
    ("Santiago 1:5", "Si alguno de vosotros tiene falta de sabiduria, pidala a Dios."),
]


def verse_of_the_day():
    """Selecciona un versiculo de forma deterministica segun el dia del ano."""
    idx = date.today().toordinal() % len(VERSES)
    return VERSES[idx]
