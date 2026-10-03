"""
Punto de entrada de la aplicacion.
Ejecutar con:  python run.py
"""

import os
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen (uso rapido en desarrollo)
    app.run(debug=app.config.get("DEBUG", True))
