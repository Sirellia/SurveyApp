from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database() if '/' in Config.MONGO_URI.split('://')[-1] else client['survey_app']

users_collection = db['users']
surveys_collection = db['surveys']
responses_collection = db['responses']

users_collection.create_index('email', unique=True)
surveys_collection.create_index('share_code', unique=True)
surveys_collection.create_index('author_id')
responses_collection.create_index('survey_id')