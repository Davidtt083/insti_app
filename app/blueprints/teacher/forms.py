from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length


class CourseForm(FlaskForm):
    title = StringField("Nombre del curso / materia", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripcion", validators=[Length(max=1000)])
    student_ids = SelectMultipleField("Inscribir alumnos (opcional)", coerce=int)
    submit = SubmitField("Crear curso")


class CourseStudentsForm(FlaskForm):
    student_ids = SelectMultipleField("Alumnos inscritos en este curso", coerce=int)
    submit = SubmitField("Guardar inscripciones")


class AssignmentForm(FlaskForm):
    course_id = SelectField("Curso / Materia", coerce=int, validators=[DataRequired()])
    title = StringField("Titulo de la tarea", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripcion", validators=[DataRequired()])
    due_date = DateTimeField(
        "Fecha limite (AAAA-MM-DD HH:MM)",
        format="%Y-%m-%d %H:%M",
        validators=[DataRequired()],
    )
    submit = SubmitField("Guardar tarea")


class GradeForm(FlaskForm):
    grade = StringField("Calificacion", validators=[DataRequired(), Length(max=10)])
    teacher_feedback = TextAreaField("Retroalimentacion", validators=[Length(max=3000)])
    submit = SubmitField("Guardar calificacion")


class AnswerForm(FlaskForm):
    answer_text = TextAreaField("Respuesta", validators=[DataRequired(), Length(min=2, max=3000)])
    submit = SubmitField("Responder")