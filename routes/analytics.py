import csv
import io
from collections import Counter
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from routes.auth import login_required
from models.survey import Survey
from models.response import Response

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/surveys/<survey_id>/results')
@login_required
def results(survey_id):
    survey = Survey.find_by_id(survey_id)

    if not survey:
        flash('Опрос не найден', 'error')
        return redirect(url_for('surveys.dashboard'))

    if str(survey['author_id']) != str(request.current_user['_id']):
        flash('У вас нет доступа', 'error')
        return redirect(url_for('surveys.dashboard'))

    responses = Response.find_by_survey(survey_id)
    total_responses = len(responses)

    analytics_data = []

    for question in survey.get('questions', []):
        q_id = str(question['_id'])
        q_type = question['type']
        q_data = {
            'question_text': question['text'],
            'type': q_type,
            'total': total_responses
        }

        values = []
        for resp in responses:
            for ans in resp.get('answers', []):
                if ans['question_id'] == q_id:
                    values.append(ans['value'])
                    break

        if q_type in ('single_choice', 'yes_no'):
            counter = Counter(values)
            labels = []
            counts = []

            if q_type == 'single_choice':
                for option in question.get('options', []):
                    labels.append(option)
                    counts.append(counter.get(option, 0))
            else:
                labels = ['Да', 'Нет']
                counts = [counter.get('yes', 0), counter.get('no', 0)]

            q_data['labels'] = labels
            q_data['counts'] = counts
            q_data['percentages'] = [
                round(c / total_responses * 100, 1) if total_responses > 0 else 0
                for c in counts
            ]

        elif q_type == 'multiple_choice':
            counter = Counter()
            for v in values:
                if isinstance(v, list):
                    counter.update(v)
                else:
                    counter[v] += 1

            labels = question.get('options', [])
            counts = [counter.get(opt, 0) for opt in labels]
            q_data['labels'] = labels
            q_data['counts'] = counts
            q_data['percentages'] = [
                round(c / total_responses * 100, 1) if total_responses > 0 else 0
                for c in counts
            ]

        elif q_type == 'rating_scale':
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                q_data['average'] = round(sum(numeric_values) / len(numeric_values), 2)
            else:
                q_data['average'] = 0

            counter = Counter(numeric_values)
            labels = ['1', '2', '3', '4', '5']
            counts = [counter.get(i, 0) for i in range(1, 6)]
            q_data['labels'] = labels
            q_data['counts'] = counts

        elif q_type == 'text':
            q_data['text_answers'] = [v for v in values if v]

        analytics_data.append(q_data)

    return render_template('analytics/results.html',
                           user=request.current_user,
                           survey=survey,
                           analytics=analytics_data,
                           total_responses=total_responses)


@analytics_bp.route('/surveys/<survey_id>/export')
@login_required
def export_csv(survey_id):
    survey = Survey.find_by_id(survey_id)

    if not survey:
        flash('Опрос не найден', 'error')
        return redirect(url_for('surveys.dashboard'))

    if str(survey['author_id']) != str(request.current_user['_id']):
        flash('У вас нет доступа', 'error')
        return redirect(url_for('surveys.dashboard'))

    responses = Response.find_by_survey(survey_id)
    questions = survey.get('questions', [])

    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    headers = ['№', 'Дата']
    for q in questions:
        headers.append(q['text'])
    writer.writerow(headers)

    for idx, resp in enumerate(responses, 1):
        row = [idx, resp['submitted_at'].strftime('%d.%m.%Y %H:%M')]

        for q in questions:
            q_id = str(q['_id'])
            value = ''
            for ans in resp.get('answers', []):
                if ans['question_id'] == q_id:
                    v = ans['value']
                    if isinstance(v, list):
                        value = ', '.join(v)
                    elif v == 'yes':
                        value = 'Да'
                    elif v == 'no':
                        value = 'Нет'
                    else:
                        value = str(v)
                    break
            row.append(value)

        writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=survey_{survey_id}.csv'
    return response