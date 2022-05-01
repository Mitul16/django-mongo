from mongoengine.errors import DoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

import bcrypt

from .models import User

# Create your views here.


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None:
        return Response({
            'status': 'error',
            'message': 'missing username field'
        }, status=HTTP_400_BAD_REQUEST)

    if password is None:
        return Response({
            'status': 'error',
            'message': 'missing password field'
        }, status=HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        user = None

    if user is None or not bcrypt.checkpw(
        password.encode('latin1'),
        user.password_hash.encode('latin1')
    ):
        return Response({
            'status': 'error',
            'error': 'invalid credentials'
        }, status=HTTP_401_UNAUTHORIZED)
    
    response = Response({
        'status': 'success',
        'message': 'logged-in successfully'
    }, status=HTTP_200_OK)

    response.set_cookie('jwt_token', User.user_to_token(user))
    return response


@api_view(['GET'])
def logout(request):
    response = Response({
        'status': 'success',
        'message': 'logged-out successfully'
    }, status=HTTP_204_NO_CONTENT)

    response.delete_cookie('jwt_token')
    return response


@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if username is None:
        return Response({
            'status': 'error',
            'message': 'missing username field'
        }, status=HTTP_400_BAD_REQUEST)

    if password is None:
        return Response({
            'status': 'error',
            'message': 'missing password field'
        }, status=HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({
            'status': 'error',
            'message': 'passwords did not match'
        }, status=HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        user = None
    else:
        return Response({
            'status': 'error',
            'message': 'username already registered'
        }, status=HTTP_403_FORBIDDEN)

    password_salt = bcrypt.gensalt(rounds=8)
    password_hash = bcrypt.hashpw(
        password.encode('latin1'),
        password_salt
    ).decode('latin1')

    user = User()
    user.username = username
    user.password_hash = password_hash
    user.save()

    return Response( {
        'status': 'success',
        'message': 'signed-up successfully'
    }, status=HTTP_201_CREATED)