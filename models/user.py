# models/user.py

from datetime import datetime, timezone
import bcrypt
from bson import ObjectId
from models import users_collection


class User:

    @staticmethod
    def create(email, password, full_name):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_doc = {
            'email': email.lower().strip(),
            'password_hash': hashed,
            'full_name': full_name.strip(),
            'created_at': datetime.now(timezone.utc)
        }

        result = users_collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return user_doc

    @staticmethod
    def find_by_email(email):
        return users_collection.find_one({'email': email.lower().strip()})

    @staticmethod
    def find_by_id(user_id):
        return users_collection.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def check_password(user_doc, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            user_doc['password_hash']
        )