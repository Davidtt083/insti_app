"""
Application Factory del Sistema de Gestion Academica - Instituto Biblico.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

from app.config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    app = Flask(__name__)

    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Asegura que exista la carpeta de subidas
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inicializa extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesion para continuar."
    login_manager.login_message_category = "warning"

    # Importa modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models  # noqa: F401

    # Registro de Blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.student import student_bp
    from app.blueprints.teacher import teacher_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/estudiante")
    app.register_blueprint(teacher_bp, url_prefix="/profesor")

    # Filtro Jinja util para mostrar fechas
    @app.template_filter("fecha")
    def format_date(value, fmt="%d/%m/%Y %H:%M"):
        if value is None:
            return "-"
        return value.strftime(fmt)

    # Manejo de errores basico
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("main/error.html", code=403, message="Acceso no autorizado"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("main/error.html", code=404, message="Pagina no encontrada"), 404

    @app.errorhandler(413)
    def too_large(e):
        from flask import render_template
        return render_template(
            "main/error.html", code=413, message="El archivo supera el tamano maximo permitido (10 MB)"
        ), 413

    return app
