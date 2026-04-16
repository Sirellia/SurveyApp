from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson import ObjectId
from routes.auth import login_required
from models.survey import Survey
from models.response import Response

surveys_bp = Blueprint('surveys', __name__)
@surveys_bp.route('/dashboard')
@login_required
def dashboard():
    user = request.current_user
    surveys = Survey.find_by_author(user['_id'])

    for survey in surveys:
        survey['responses_count'] = Response.count_by_survey(survey['_id'])

    return render_template('dashboard/index.html',
                           user=user, surveys=surveys)


@surveys_bp.route('/surveys/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Введите название опроса', 'error')
            return render_template('dashboard/create.html',
                                   user=request.current_user)

        survey = Survey.create(
            author_id=request.current_user['_id'],
            title=title,
            description=description
        )

        flash('Опрос создан! Теперь добавьте вопросы.', 'success')
        return redirect(url_for('surveys.edit_survey',
                                survey_id=survey['_id']))

    return render_template('dashboard/create.html',
                           user=request.current_user)


@surveys_bp.route('/surveys/<survey_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    survey = Survey.find_by_id(survey_id)

    if not survey:
        flash('Опрос не найден', 'error')
        return redirect(url_for('surveys.dashboard'))

    if str(survey['author_id']) != str(request.current_user['_id']):
        flash('У вас нет доступа к этому опросу', 'error')
        return redirect(url_for('surveys.dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_question':
            q_text = request.form.get('question_text', '').strip()
            q_type = request.form.get('question_type', 'text')
            q_required = request.form.get('is_required') == 'on'
            q_has_correct = request.form.get('has_correct_answer') == 'on'

            if not q_text:
                flash('Введите текст вопроса', 'error')
            else:
                question = {
                    'text': q_text,
                    'type': q_type,
                    'is_required': q_required,
                    'has_correct_answer': q_has_correct,
                    'correct_answer': None,
                    'options': []
                }

                if q_type in ('single_choice', 'multiple_choice'):
                    options = request.form.getlist('options[]')
                    options = [o.strip() for o in options if o.strip()]
                    if len(options) < 2:
                        flash('Добавьте минимум 2 варианта ответа', 'error')
                        survey = Survey.find_by_id(survey_id)
                        survey['responses_count'] = Response.count_by_survey(
                            survey['_id']
                        )
                        return render_template('dashboard/edit.html',
                                               user=request.current_user,
                                               survey=survey)
                    question['options'] = options

                    if q_has_correct:
                        if q_type == 'single_choice':
                            correct = request.form.get('correct_answer', '')
                            question['correct_answer'] = correct
                        elif q_type == 'multiple_choice':
                            correct = request.form.getlist('correct_answers[]')
                            question['correct_answer'] = correct

                elif q_type == 'yes_no' and q_has_correct:
                    correct = request.form.get('correct_answer', '')
                    question['correct_answer'] = correct

                Survey.add_question(survey_id, question)
                flash('Вопрос добавлен!', 'success')

        elif action == 'delete_question':
            question_id = request.form.get('question_id')
            Survey.delete_question(survey_id, question_id)
            flash('Вопрос удалён', 'info')

        elif action == 'update_status':
            new_status = request.form.get('status')
            if new_status in ('draft', 'active', 'closed'):
                survey_data = Survey.find_by_id(survey_id)
                if new_status == 'active' and len(
                    survey_data.get('questions', [])
                ) == 0:
                    flash('Нельзя опубликовать опрос без вопросов', 'error')
                else:
                    Survey.update(survey_id, {'status': new_status})
                    status_names = {
                        'draft': 'черновик',
                        'active': 'активный',
                        'closed': 'закрыт'
                    }
                    flash(
                        f'Статус изменён: {status_names[new_status]}',
                        'success'
                    )

        elif action == 'update_info':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            if title:
                Survey.update(survey_id, {
                    'title': title,
                    'description': description
                })
                flash('Информация обновлена', 'success')

        return redirect(url_for('surveys.edit_survey', survey_id=survey_id))

    survey['responses_count'] = Response.count_by_survey(survey['_id'])
    return render_template('dashboard/edit.html',
                           user=request.current_user, survey=survey)


@surveys_bp.route('/surveys/<survey_id>/delete', methods=['POST'])
@login_required
def delete_survey(survey_id):
    survey = Survey.find_by_id(survey_id)

    if not survey:
        flash('Опрос не найден', 'error')
        return redirect(url_for('surveys.dashboard'))

    if str(survey['author_id']) != str(request.current_user['_id']):
        flash('У вас нет доступа', 'error')
        return redirect(url_for('surveys.dashboard'))

    Response.delete_by_survey(survey_id)
    Survey.delete(survey_id)

    flash('Опрос удалён', 'info')
    return redirect(url_for('surveys.dashboard'))