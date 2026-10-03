"""
Decoradores personalizados de control de acceso.
"""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(role):
    """
    Restringe una vista a usuarios autenticados con un rol especifico.
    Uso: @role_required('profesor')  o  @role_required('estudiante')
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesion para acceder a esta pagina.", "warning")
                return redirect(url_for("auth.login"))
            if current_user.role != role:
                flash("No tienes permiso para acceder a esta seccion.", "danger")
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
