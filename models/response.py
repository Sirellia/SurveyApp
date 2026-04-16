from datetime import datetime, timezone
from bson import ObjectId
from models import responses_collection


class Response:

    @staticmethod
    def create(survey_id, answers, score=0, total_questions=0):
        response_doc = {
            'survey_id': ObjectId(survey_id),
            'answers': answers,
            'score': score,
            'total_questions': total_questions,
            'submitted_at': datetime.now(timezone.utc)
        }
        result = responses_collection.insert_one(response_doc)
        response_doc['_id'] = result.inserted_id
        return response_doc

    @staticmethod
    def find_by_survey(survey_id):
        return list(responses_collection.find(
            {'survey_id': ObjectId(survey_id)}
        ).sort('submitted_at', -1))

    @staticmethod
    def count_by_survey(survey_id):
        return responses_collection.count_documents(
            {'survey_id': ObjectId(survey_id)}
        )

    @staticmethod
    def delete_by_survey(survey_id):
        responses_collection.delete_many(
            {'survey_id': ObjectId(survey_id)}
        )