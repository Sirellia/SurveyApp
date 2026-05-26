from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.survey import Survey
from models.response import Response
from bson import ObjectId
from datetime import datetime

public_bp = Blueprint('public_bp', __name__)


# ─── КАТАЛОГ АКТИВНЫХ ОПРОСОВ ─────────────────────────────────────────────────

@public_bp.route('/catalog')
def catalog():
    """Публичная страница: все опубликованные активные опросы."""
    surveys = list(db.surveys.find(
        {'status': 'active'},
        {
            'title': 1,
            'description': 1,
            'share_code': 1,
            'questions': 1,
            'created_at': 1
        }
    ).sort('created_at', -1))
    return render_template('catalog.html', surveys=surveys)


# ─── ПРОХОЖДЕНИЕ ОПРОСА ───────────────────────────────────────────────────────

@public_bp.route('/s/<share_code>', methods=['GET', 'POST'])
def take_survey(share_code):
    survey_doc = db.surveys.find_one({'share_code': share_code})

    if not survey_doc:
        return render_template('404_survey.html'), 404

    if survey_doc['status'] == 'draft':
        return render_template('survey_not_published.html', survey=survey_doc)

    if survey_doc['status'] == 'closed':
        return render_template('survey_closed.html', survey=survey_doc)

    if request.method == 'POST':
        questions  = survey_doc.get('questions', [])
        answers    = []
        errors     = []
        score      = 0
        total_scored = 0

        for q in questions:
            qid  = str(q['_id'])
            qtype = q['type']

            # Извлечение ответа из формы
            if qtype == 'multiple_choice':
                value = request.form.getlist(f'q_{qid}')
            elif qtype == 'rating_scale':
                raw = request.form.get(f'q_{qid}', '')
                value = int(raw) if raw.isdigit() else None
            else:
                value = request.form.get(f'q_{qid}', '').strip()

            # Проверка обязательных вопросов
            is_empty = (value is None) or (value == '') or (value == [])
            if q.get('is_required') and is_empty:
                errors.append(f'Вопрос «{q["text"]}» обязателен для ответа.')

            # Проверка правильного ответа (режим теста)
            is_correct = None
            if q.get('has_correct_answer') and q.get('correct_answer') not in (None, '', []):
                total_scored += 1
                if qtype == 'multiple_choice':
                    is_correct = sorted(value) == sorted(q['correct_answer'])
                else:
                    is_correct = str(value) == str(q['correct_answer'])
                if is_correct:
                    score += 1

            answers.append({
                '_id':        q['_id'],
                'question':   q['text'],
                'type':       qtype,
                'value':      value,
                'is_correct': is_correct,
                'correct_answer': q.get('correct_answer')
            })

        if errors:
            return render_template(
                'take.html',
                survey=survey_doc,
                errors=errors,
                form_data=request.form
            )

        # Сохранение ответа
        response_doc = {
            'survey_id':       survey_doc['_id'],
            'answers':         answers,
            'score':           score,
            'total_questions': total_scored,
            'submitted_at':    datetime.utcnow()
        }
        db.responses.insert_one(response_doc)

        is_test = total_scored > 0
        return render_template(
            'thanks.html',
            survey=survey_doc,
            score=score,
            total=total_scored,
            answers=answers,
            is_test=is_test
        )

    return render_template('take.html', survey=survey_doc, errors=[], form_data={})