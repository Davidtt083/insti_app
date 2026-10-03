"""
Modelos de datos (SQLAlchemy) del Sistema de Gestion Academica.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tabla intermedia para inscripcion de alumnos en cursos (Muchos a Muchos)
course_enrollments = db.Table(
    "course_enrollments",
    db.Column("student_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'profesor' o 'estudiante'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    courses_taught = db.relationship(
        "Course", backref="teacher", lazy=True, foreign_keys="Course.teacher_id"
    )
    submissions = db.relationship(
        "Submission", backref="student", lazy=True, foreign_keys="Submission.student_id"
    )
    questions_asked = db.relationship(
        "Question", backref="student", lazy=True, foreign_keys="Question.student_id"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_teacher(self):
        return self.role == "profesor"

    @property
    def is_student(self):
        return self.role == "estudiante"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Course(db.Model):
    """Materia / curso, ej. Hermeneutica, Teologia Sistematica."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacion de estudiantes inscritos
    students = db.relationship(
        "User",
        secondary=course_enrollments,
        backref=db.backref("enrolled_courses", lazy=True),
        lazy=True,
    )

    assignments = db.relationship(
        "Assignment", backref="course", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Course {self.title}>"


class Assignment(db.Model):
    """Tarea o proyecto asociado a un curso."""

    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship(
        "Submission", backref="assignment", lazy=True, cascade="all, delete-orphan"
    )
    questions = db.relationship(
        "Question", backref="assignment", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Assignment {self.title}>"


class Submission(db.Model):
    """Entrega de un estudiante para una tarea."""

    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    grade = db.Column(db.String(10), nullable=True)
    teacher_feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)

    @property
    def status(self):
        if self.grade is not None:
            return "Calificada"
        if self.assignment and self.submitted_at > self.assignment.due_date:
            return "Entregada con retraso"
        return "A tiempo"

    def __repr__(self):
        return f"<Submission {self.id} - assignment {self.assignment_id}>"


class Question(db.Model):
    """Duda o consulta de un estudiante sobre una tarea."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    answered_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), default="pendiente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime, nullable=True)

    teacher = db.relationship("User", foreign_keys=[answered_by])

    def __repr__(self):
        return f"<Question {self.id} - {self.status}>"