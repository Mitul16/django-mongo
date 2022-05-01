from functools import wraps

from bson.objectid import ObjectId
from bson.errors import InvalidId

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST


def get_form_id(func):
    '''
    Passes `request` along with the `form_id` to the wrappee
    '''
    @wraps(func)
    def inner(request, form_id, *args, **kwargs):
        try:
            form_id = ObjectId(form_id)
        except InvalidId:
            return Response({
                'status': 'error',
                'message': 'invalid form id'
            }, status=HTTP_400_BAD_REQUEST)
            
        return func(request, *args, form_id=form_id, **kwargs)

    return inner