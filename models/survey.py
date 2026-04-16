# models/survey.py

from datetime import datetime, timezone
import secrets
from bson import ObjectId
from models import surveys_collection


class Survey:

    @staticmethod
    def create(author_id, title, description=''):
        share_code = secrets.token_urlsafe(8)

        while surveys_collection.find_one({'share_code': share_code}):
            share_code = secrets.token_urlsafe(8)

        survey_doc = {
            'author_id': ObjectId(author_id),
            'title': title.strip(),
            'description': description.strip(),
            'share_code': share_code,
            'status': 'draft',  # draft, active, closed
            'is_anonymous': True,
            'questions': [],  # Вопросы хранятся внутри опроса
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }

        result = surveys_collection.insert_one(survey_doc)
        survey_doc['_id'] = result.inserted_id
        return survey_doc

    @staticmethod
    def find_by_id(survey_id):
        return surveys_collection.find_one({'_id': ObjectId(survey_id)})

    @staticmethod
    def find_by_share_code(share_code):
        return surveys_collection.find_one({'share_code': share_code})

    @staticmethod
    def find_by_author(author_id):
        return list(surveys_collection.find(
            {'author_id': ObjectId(author_id)}
        ).sort('created_at', -1))

    @staticmethod
    def update(survey_id, update_data):
        update_data['updated_at'] = datetime.now(timezone.utc)
        surveys_collection.update_one(
            {'_id': ObjectId(survey_id)},
            {'$set': update_data}
        )

    @staticmethod
    def delete(survey_id):
        surveys_collection.delete_one({'_id': ObjectId(survey_id)})

    @staticmethod
    def add_question(survey_id, question):
        question['_id'] = ObjectId()
        question['created_at'] = datetime.now(timezone.utc)

        surveys_collection.update_one(
            {'_id': ObjectId(survey_id)},
            {
                '$push': {'questions': question},
                '$set': {'updated_at': datetime.now(timezone.utc)}
            }
        )
        return question

    @staticmethod
    def delete_question(survey_id, question_id):
        surveys_collection.update_one(
            {'_id': ObjectId(survey_id)},
            {
                '$pull': {'questions': {'_id': ObjectId(question_id)}},
                '$set': {'updated_at': datetime.now(timezone.utc)}
            }
        )

    @staticmethod
    def count_responses(survey_id):
        from models import responses_collection
        return responses_collection.count_documents(
            {'survey_id': ObjectId(survey_id)}
        )