from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    name = StringField("Nombre completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Correo electronico", validators=[DataRequired(), Email(), Length(max=150)])
    role = SelectField(
        "Rol",
        choices=[("estudiante", "Estudiante"), ("profesor", "Profesor")],
        validators=[DataRequired()],
    )
    password = PasswordField("Contrasena", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmar contrasena",
        validators=[DataRequired(), EqualTo("password", message="Las contrasenas no coinciden")],
    )
    submit = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    email = StringField("Correo electronico", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasena", validators=[DataRequired()])
    submit = SubmitField("Iniciar sesion")
