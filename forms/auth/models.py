from mongoengine import Document
from mongoengine.fields import (
    StringField
)

from bson.objectid import ObjectId
import jwt
from jwt.exceptions import PyJWTError
from mongoengine.errors import DoesNotExist

import forms.settings as settings

# Create your models here.


class User(Document):
    username = StringField(max_length=255)
    password_hash = StringField(max_length=255)

    @staticmethod
    def user_to_token(user):
        data = {
            'id': str(user.id)
        }

        return jwt.encode(data, key=settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def user_from_token(jwt_token):
        try:
            data = jwt.decode(jwt_token, key=settings.SECRET_KEY, algorithms=['HS256'])
        except PyJWTError:
            return None
        else:
            try:
                return User.objects.get(id=ObjectId(data['id']))
            except DoesNotExist:
                return None

    @staticmethod
    def user_id_from_token(jwt_token):
        try:
            data = jwt.decode(jwt_token, key=settings.SECRET_KEY, algorithms=['HS256'])
            return ObjectId(data['id'])
        except PyJWTError:
            return None