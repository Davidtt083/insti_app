"""
Script de poblado inicial (seed) para pruebas rapidas.
"""

from datetime import datetime, timedelta

from app import create_app, db
from app.models import User, Course, Assignment

app = create_app("development")

with app.app_context():
    db.create_all()

    # --- Profesor ---
    teacher = User.query.filter_by(email="profesor@institutobiblico.edu").first()
    if not teacher:
        teacher = User(
            name="Pastor Juan Perez",
            email="profesor@institutobiblico.edu",
            role="profesor",
        )
        teacher.set_password("Profesor123")
        db.session.add(teacher)
        db.session.commit()
        print("Profesor creado: profesor@institutobiblico.edu / Profesor123")
    else:
        print("El profesor de prueba ya existia.")

    # --- Estudiante ---
    student = User.query.filter_by(email="estudiante@institutobiblico.edu").first()
    if not student:
        student = User(
            name="Maria Gonzalez",
            email="estudiante@institutobiblico.edu",
            role="estudiante",
        )
        student.set_password("Estudiante123")
        db.session.add(student)
        db.session.commit()
        print("Estudiante creado: estudiante@institutobiblico.edu / Estudiante123")
    else:
        print("El estudiante de prueba ya existia.")

    # --- Cursos ---
    course1 = Course.query.filter_by(title="Hermeneutica Biblica").first()
    if not course1:
        course1 = Course(
            title="Hermeneutica Biblica",
            description="Principios de interpretacion de las Escrituras.",
            teacher_id=teacher.id,
        )
        db.session.add(course1)

    course2 = Course.query.filter_by(title="Teologia Sistematica I").first()
    if not course2:
        course2 = Course(
            title="Teologia Sistematica I",
            description="Doctrinas fundamentales de la fe cristiana.",
            teacher_id=teacher.id,
        )
        db.session.add(course2)

    db.session.commit()

    # Inscribir estudiante de prueba en ambos cursos
    if student not in course1.students:
        course1.students.append(student)
    if student not in course2.students:
        course2.students.append(student)

    db.session.commit()
    print("Cursos creados/verificados e inscripciones asignadas.")

    # --- Tareas ---
    if not Assignment.query.filter_by(title="Analisis exegetico de Filipenses 2").first():
        db.session.add(
            Assignment(
                course_id=course1.id,
                title="Analisis exegetico de Filipenses 2",
                description="Realiza un analisis exegetico del pasaje, identificando contexto historico y aplicacion.",
                due_date=datetime.utcnow() + timedelta(days=7),
            )
        )

    if not Assignment.query.filter_by(title="Ensayo sobre la doctrina de la Trinidad").first():
        db.session.add(
            Assignment(
                course_id=course2.id,
                title="Ensayo sobre la doctrina de la Trinidad",
                description="Escribe un ensayo de al menos 3 paginas sobre la doctrina de la Trinidad.",
                due_date=datetime.utcnow() + timedelta(days=10),
            )
        )

    db.session.commit()
    print("Tareas de ejemplo creadas/verificadas.")
    print("\nListo. Ya puedes iniciar sesion con las credenciales de prueba.")