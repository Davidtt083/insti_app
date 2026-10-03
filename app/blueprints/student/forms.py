from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class SubmissionForm(FlaskForm):
    file = FileField(
        "Archivo de la entrega",
        validators=[
            FileRequired(message="Debes adjuntar un archivo."),
            FileAllowed(["pdf", "docx", "doc", "jpg", "jpeg", "png"], "Formato de archivo no permitido."),
        ],
    )
    submit = SubmitField("Enviar entrega")


class QuestionForm(FlaskForm):
    question_text = TextAreaField(
        "Tu pregunta", validators=[DataRequired(), Length(min=5, max=2000)]
    )
    submit = SubmitField("Enviar pregunta")
