from datetime import datetime

from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app import db
from app.blueprints.student import student_bp
from app.blueprints.student.forms import SubmissionForm, QuestionForm
from app.decorators import role_required
from app.models import Assignment, Submission, Question
from app.utils import save_upload, verse_of_the_day


@student_bp.route("/dashboard")
@login_required
@role_required("estudiante")
def dashboard():
    verse_ref, verse_text = verse_of_the_day()

    enrolled_course_ids = [c.id for c in current_user.enrolled_courses]

    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    graded_count = sum(1 for s in submissions if s.grade is not None)

    submitted_assignment_ids = {s.assignment_id for s in submissions}
    total_assignments = (
        Assignment.query.filter(Assignment.course_id.in_(enrolled_course_ids)).count()
        if enrolled_course_ids
        else 0
    )
    pending_count = max(total_assignments - len(submitted_assignment_ids), 0)

    answered_questions = Question.query.filter_by(
        student_id=current_user.id, status="respondida"
    ).count()

    return render_template(
        "student/dashboard.html",
        verse_ref=verse_ref,
        verse_text=verse_text,
        pending_count=pending_count,
        graded_count=graded_count,
        answered_questions=answered_questions,
    )


@student_bp.route("/tareas")
@login_required
@role_required("estudiante")
def tasks():
    enrolled_course_ids = [c.id for c in current_user.enrolled_courses]
    assignments = (
        Assignment.query.filter(Assignment.course_id.in_(enrolled_course_ids))
        .order_by(Assignment.due_date.asc())
        .all()
        if enrolled_course_ids
        else []
    )
    my_submissions = {
        s.assignment_id: s
        for s in Submission.query.filter_by(student_id=current_user.id).all()
    }
    return render_template(
        "student/tasks.html", assignments=assignments, my_submissions=my_submissions
    )


@student_bp.route("/tareas/<int:assignment_id>/entregar", methods=["GET", "POST"])
@login_required
@role_required("estudiante")
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    # Validacion: el alumno debe estar inscrito en el curso de esta tarea
    if assignment.course not in current_user.enrolled_courses:
        abort(403)

    existing = Submission.query.filter_by(
        assignment_id=assignment.id, student_id=current_user.id
    ).first()
    if existing and existing.grade is not None:
        flash("Esta tarea ya fue calificada y no se puede reenviar.", "warning")
        return redirect(url_for("student.tasks"))

    form = SubmissionForm()
    if form.validate_on_submit():
        relative_path, ext = save_upload(form.file.data, subfolder="submissions")
        if relative_path is None:
            flash("Archivo invalido. Formatos permitidos: pdf, docx, doc, jpg, jpeg, png.", "danger")
            return render_template("student/submit.html", form=form, assignment=assignment)

        if existing:
            existing.file_path = relative_path
            existing.file_type = ext
            existing.submitted_at = datetime.utcnow()
        else:
            existing = Submission(
                assignment_id=assignment.id,
                student_id=current_user.id,
                file_path=relative_path,
                file_type=ext,
            )
            db.session.add(existing)

        db.session.commit()
        flash("Entrega enviada correctamente.", "success")
        return redirect(url_for("student.tasks"))

    return render_template("student/submit.html", form=form, assignment=assignment)


@student_bp.route("/calificaciones")
@login_required
@role_required("estudiante")
def grades():
    submissions = (
        Submission.query.filter_by(student_id=current_user.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return render_template("student/grades.html", submissions=submissions)


@student_bp.route("/tareas/<int:assignment_id>/consultas", methods=["GET", "POST"])
@login_required
@role_required("estudiante")
def questions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    # Validacion: el alumno debe estar inscrito en el curso
    if assignment.course not in current_user.enrolled_courses:
        abort(403)

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            assignment_id=assignment.id,
            student_id=current_user.id,
            question_text=form.question_text.data.strip(),
        )
        db.session.add(question)
        db.session.commit()
        flash("Pregunta enviada al profesor.", "success")
        return redirect(url_for("student.questions", assignment_id=assignment.id))

    my_questions = (
        Question.query.filter_by(assignment_id=assignment.id, student_id=current_user.id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return render_template(
        "student/questions.html", assignment=assignment, form=form, questions=my_questions
    )

@student_bp.route("/consultas")
@login_required
@role_required("estudiante")
def my_questions():
    questions = (
        Question.query.filter_by(student_id=current_user.id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return render_template("student/my_questions.html", questions=questions)