import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/survey_app')