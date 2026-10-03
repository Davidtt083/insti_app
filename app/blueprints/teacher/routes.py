from datetime import datetime

from flask import render_template, redirect, url_for, flash, abort, send_from_directory, current_app, request
from flask_login import login_required, current_user

from app import db
from app.blueprints.teacher import teacher_bp
from app.blueprints.teacher.forms import AssignmentForm, CourseForm, CourseStudentsForm, GradeForm, AnswerForm
from app.decorators import role_required
from app.models import Course, Assignment, Submission, Question, User
from app.utils import verse_of_the_day


@teacher_bp.route("/dashboard")
@login_required
@role_required("profesor")
def dashboard():
    verse_ref, verse_text = verse_of_the_day()

    my_course_ids = [c.id for c in Course.query.filter_by(teacher_id=current_user.id).all()]

    pending_grading = 0
    unanswered_questions = 0
    if my_course_ids:
        assignment_ids = [
            a.id for a in Assignment.query.filter(Assignment.course_id.in_(my_course_ids)).all()
        ]
        if assignment_ids:
            pending_grading = Submission.query.filter(
                Submission.assignment_id.in_(assignment_ids), Submission.grade.is_(None)
            ).count()
            unanswered_questions = Question.query.filter(
                Question.assignment_id.in_(assignment_ids), Question.status == "pendiente"
            ).count()

    return render_template(
        "teacher/dashboard.html",
        verse_ref=verse_ref,
        verse_text=verse_text,
        pending_grading=pending_grading,
        unanswered_questions=unanswered_questions,
        course_count=len(my_course_ids),
    )


@teacher_bp.route("/cursos", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def courses():
    form = CourseForm()
    students_list = User.query.filter_by(role="estudiante").order_by(User.name).all()
    form.student_ids.choices = [(s.id, f"{s.name} ({s.email})") for s in students_list]

    if form.validate_on_submit():
        course = Course(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            teacher_id=current_user.id,
        )
        if form.student_ids.data:
            selected_students = User.query.filter(
                User.id.in_(form.student_ids.data), User.role == "estudiante"
            ).all()
            course.students = selected_students

        db.session.add(course)
        db.session.commit()
        flash("Curso creado correctamente.", "success")
        return redirect(url_for("teacher.courses"))

    my_courses = Course.query.filter_by(teacher_id=current_user.id).order_by(Course.title).all()
    return render_template("teacher/courses.html", form=form, courses=my_courses)


@teacher_bp.route("/cursos/<int:course_id>/estudiantes", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def course_students(course_id):
    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        abort(403)

    form = CourseStudentsForm()
    all_students = User.query.filter_by(role="estudiante").order_by(User.name).all()
    form.student_ids.choices = [(s.id, f"{s.name} ({s.email})") for s in all_students]

    if request.method == "GET":
        form.student_ids.data = [s.id for s in course.students]

    if form.validate_on_submit():
        if form.student_ids.data:
            selected_students = User.query.filter(
                User.id.in_(form.student_ids.data), User.role == "estudiante"
            ).all()
            course.students = selected_students
        else:
            course.students = []

        db.session.commit()
        flash("Lista de alumnos inscritos actualizada exitosamente.", "success")
        return redirect(url_for("teacher.course_students", course_id=course.id))

    return render_template("teacher/course_students.html", course=course, form=form)


@teacher_bp.route("/tareas", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def assignments():
    my_courses = Course.query.filter_by(teacher_id=current_user.id).all()

    form = AssignmentForm()
    form.course_id.choices = [(c.id, c.title) for c in my_courses]

    if not my_courses:
        flash("Primero crea un curso antes de agregar tareas.", "warning")
        return redirect(url_for("teacher.courses"))

    if form.validate_on_submit():
        course = Course.query.get(form.course_id.data)
        if course is None or course.teacher_id != current_user.id:
            abort(403)

        assignment = Assignment(
            course_id=course.id,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            due_date=form.due_date.data,
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Tarea publicada correctamente.", "success")
        return redirect(url_for("teacher.assignments"))

    my_course_ids = [c.id for c in my_courses]
    all_assignments = (
        Assignment.query.filter(Assignment.course_id.in_(my_course_ids))
        .order_by(Assignment.due_date.desc())
        .all()
    )
    return render_template("teacher/assignments.html", form=form, assignments=all_assignments)


@teacher_bp.route("/entregas/<int:assignment_id>")
@login_required
@role_required("profesor")
def review_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if assignment.course.teacher_id != current_user.id:
        abort(403)

    submissions = (
        Submission.query.filter_by(assignment_id=assignment.id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return render_template(
        "teacher/submissions.html", assignment=assignment, submissions=submissions
    )


@teacher_bp.route("/entregas/archivo/<int:submission_id>")
@login_required
@role_required("profesor")
def download_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.teacher_id != current_user.id:
        abort(403)

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], submission.file_path, as_attachment=True
    )


@teacher_bp.route("/entregas/<int:submission_id>/calificar", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def grade_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.teacher_id != current_user.id:
        abort(403)

    form = GradeForm(obj=submission)
    if form.validate_on_submit():
        submission.grade = form.grade.data.strip()
        submission.teacher_feedback = form.teacher_feedback.data.strip() if form.teacher_feedback.data else None
        submission.graded_at = datetime.utcnow()
        db.session.commit()
        flash("Calificacion guardada.", "success")
        return redirect(url_for("teacher.review_submissions", assignment_id=submission.assignment_id))

    return render_template("teacher/grade_submission.html", form=form, submission=submission)


@teacher_bp.route("/consultas")
@login_required
@role_required("profesor")
def questions_inbox():
    my_course_ids = [c.id for c in Course.query.filter_by(teacher_id=current_user.id).all()]
    assignment_ids = [
        a.id for a in Assignment.query.filter(Assignment.course_id.in_(my_course_ids)).all()
    ]
    pending = (
        Question.query.filter(
            Question.assignment_id.in_(assignment_ids), Question.status == "pendiente"
        )
        .order_by(Question.created_at.asc())
        .all()
        if assignment_ids
        else []
    )
    answered = (
        Question.query.filter(
            Question.assignment_id.in_(assignment_ids), Question.status == "respondida"
        )
        .order_by(Question.answered_at.desc())
        .all()
        if assignment_ids
        else []
    )
    return render_template("teacher/questions.html", pending=pending, answered=answered)


@teacher_bp.route("/consultas/<int:question_id>/responder", methods=["GET", "POST"])
@login_required
@role_required("profesor")
def answer_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.assignment.course.teacher_id != current_user.id:
        abort(403)

    form = AnswerForm()
    if form.validate_on_submit():
        question.answer_text = form.answer_text.data.strip()
        question.answered_by = current_user.id
        question.status = "respondida"
        question.answered_at = datetime.utcnow()
        db.session.commit()
        flash("Respuesta enviada al estudiante.", "success")
        return redirect(url_for("teacher.questions_inbox"))

    return render_template("teacher/answer_question.html", form=form, question=question)