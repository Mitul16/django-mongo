from functools import wraps

from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED

from .models import User


def get_user_id(func):
    '''
    Decodes the JWT token, if any, into ID of the
    User collection.
    
    Passes `request` along with the `user_id` to the wrappee
    '''
    @wraps(func)
    def inner(request, *args, **kwargs):
        jwt_token = request.COOKIES.get('jwt_token')
        user_id = User.user_id_from_token(jwt_token)

        if user_id is None:
            return Response({
                'status': 'error',
                'message': 'Please login first!'
            }, status=HTTP_401_UNAUTHORIZED)

        return func(request, *args, user_id=user_id, **kwargs)

    return inner