from flask import Blueprint, render_template, request, flash
from models.survey import Survey
from models.response import Response

public_bp = Blueprint('public', __name__)


@public_bp.route('/s/<share_code>', methods=['GET', 'POST'])
def take_survey(share_code):
    survey = Survey.find_by_share_code(share_code)

    if not survey:
        return render_template('survey/closed.html',
                               message='Опрос не найден')

    if survey['status'] == 'closed':
        return render_template('survey/closed.html',
                               message='Этот опрос завершён')

    if survey['status'] == 'draft':
        return render_template('survey/closed.html',
                               message='Этот опрос ещё не опубликован')

    if request.method == 'POST':
        answers = []
        errors = []
        score = 0
        total_scored_questions = 0

        for question in survey.get('questions', []):
            q_id = str(question['_id'])
            q_type = question['type']

            if q_type == 'text':
                value = request.form.get(f'q_{q_id}', '').strip()
            elif q_type == 'single_choice':
                value = request.form.get(f'q_{q_id}', '')
            elif q_type == 'multiple_choice':
                value = request.form.getlist(f'q_{q_id}')
            elif q_type == 'rating_scale':
                value = request.form.get(f'q_{q_id}', '')
                if value:
                    value = int(value)
            elif q_type == 'yes_no':
                value = request.form.get(f'q_{q_id}', '')
            else:
                value = request.form.get(f'q_{q_id}', '')

            if question.get('is_required', True):
                if not value or (isinstance(value, list) and len(value) == 0):
                    errors.append(f'Ответьте на вопрос: "{question["text"]}"')

            is_correct = None
            if question.get('has_correct_answer') and question.get('correct_answer'):
                total_scored_questions += 1
                correct = question['correct_answer']

                if q_type == 'multiple_choice':
                    if isinstance(value, list) and isinstance(correct, list):
                        is_correct = sorted(value) == sorted(correct)
                    else:
                        is_correct = False
                else:
                    is_correct = str(value) == str(correct)

                if is_correct:
                    score += 1

            answers.append({
                'question_id': q_id,
                'question_text': question['text'],
                'question_type': q_type,
                'value': value,
                'is_correct': is_correct
            })

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('survey/take.html', survey=survey)

        Response.create(
            survey_id=survey['_id'],
            answers=answers,
            score=score,
            total_questions=total_scored_questions
        )

        return render_template('survey/thanks.html',
                               survey=survey,
                               score=score,
                               total_questions=total_scored_questions,
                               answers=answers)

    return render_template('survey/take.html', survey=survey)