from mongoengine.errors import DoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

import pandas

from .models import (
    FormFieldEntry,
    FormField,
    Form,
    FormEntry
)

from auth.middlewares import get_user_id
from .middlewares import get_form_id

# Create your views here.


@api_view(['POST'])
@get_user_id
def create_form(request, user_id):
    if "file" not in request.FILES:
        return Response({
            'status': 'error',
            'message': 'missing CSV file'
        }, status=HTTP_400_BAD_REQUEST)

    form_name = request.data.get('name')
    
    if form_name is None:
        return Response({
            'status': 'error',
            'message': 'missing form name'
        }, status=HTTP_400_BAD_REQUEST)

    form_data = pandas.read_csv(request.FILES['file'])
    fields = {}

    for _, field in form_data.iterrows():
        field_name = field.get('name')

        if field_name is None:
            return Response({
                'status': 'error',
                'message': f'duplicate field found: {field}'
            }, status=HTTP_400_BAD_REQUEST)

        if field_name in fields:
            return Response({
                'status': 'error',
                'message': f'duplicate field found: {field}'
            }, status=HTTP_400_BAD_REQUEST)

        form_field = FormField.from_dict(field.to_dict())

        if form_field is None:
            return Response({
                'status': 'error',
                'message': 'invalid form'
            }, status=HTTP_400_BAD_REQUEST)
        
        fields[field_name] = form_field
    
    form = Form(name=form_name, owner_id=user_id, fields=fields.values())
    form.save()
    
    return Response({
        'status': 'success',
        'message': 'form created successfully',
        'data': { 'form_id': str(form.id) }
    }, status=HTTP_201_CREATED)


@api_view(['DELETE'])
@get_user_id
def delete_form(request, user_id, form_id):
    try:
        form = Form.objects.get(id=form_id)
    except DoesNotExist:        
        return Response({
            'status': 'error',
            'message': 'form not found',
        }, status=HTTP_404_NOT_FOUND)

    print(user_id, form_id, form.owner_id)

    if user_id != form.owner_id:
        return Response({
            'status': 'error',
            'message': 'only the owner of the form can delete it',
        }, status=HTTP_403_FORBIDDEN)
    
    form.delete()

    return Response({
        'status': 'success',
        'message': 'form deleted successfully',
    }, status=HTTP_200_OK)


@api_view(['GET'])
@get_user_id
@get_form_id
def get_form(request, user_id, form_id):
    try:
        form = Form.objects.get(owner_id=user_id, id=form_id)
    except DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'form not found',
        }, status=HTTP_404_NOT_FOUND)

    return Response({
        'status': 'success',
        'message': 'form fetched successfully',
        'data': form.to_dict()
    }, status=HTTP_200_OK)


@api_view(['POST'])
@get_user_id
@get_form_id
def update_form(request, user_id, form_id):
    # values - from, to
    # actions - add, update, delete
    # - add
    #   - from: None, to: not None
    # - update
    #   - from: not None, to: not None
    # - delete
    #   - from: not None, to: None

    try:
        form = Form.objects.get(owner_id=user_id, id=form_id)
    except DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'form not found',
        }, status=HTTP_404_NOT_FOUND)

    changes = request.data
    fields = {}

    for field in form.fields:
        fields[field.name] = field

    if changes is None:
        return Response({
            'status': 'error',
            'message': 'no changes provided',
        }, status=HTTP_400_BAD_REQUEST)

    for change in changes:
        from_field_name = change.get('from')
        form_field_to = change.get('to')

        if from_field_name is None and form_field_to is None:
            return Response({
                'status': 'error',
                'message': 'invalid update'
            }, status=HTTP_400_BAD_REQUEST)

        # action: add
        if from_field_name is None:
            form_field_new = FormField.from_dict(form_field_to)

            if form_field_new is None:
                return Response({
                    'status': 'error',
                    'message': 'invalid update',
                }, status=HTTP_400_BAD_REQUEST)

            if form_field_new.name in fields:
                return Response({
                    'status': 'error',
                    'message': f'duplicate field found: {form_field_new.name}'
                }, status=HTTP_400_BAD_REQUEST)
                    
            fields[form_field_new.name] = form_field_new
        # action: delete
        elif form_field_to is None:
            if from_field_name not in fields:
                return Response({
                    'status': 'error',
                    'message': f'field not found: {from_field_name}'
                }, status=HTTP_400_BAD_REQUEST)

            del fields[from_field_name]
        # action: update
        else:
            if from_field_name not in fields:
                return Response({
                    'status': 'error',
                    'message': f'field not found: {from_field_name}'
                }, status=HTTP_400_BAD_REQUEST)

            form_field_new = FormField.from_dict(form_field_to)
            
            if form_field_new is None:
                return Response({
                    'status': 'error',
                    'message': 'invalid update',
                }, status=HTTP_400_BAD_REQUEST)

            if form_field_new.name in fields:
                return Response({
                    'status': 'error',
                    'message': f'duplicate field found: {form_field_new.name}'
                }, status=HTTP_400_BAD_REQUEST)
                    
            fields[from_field_name] = form_field_new

    # update and re-populate the fields in the instance / object
    form.update(fields=fields.values())
    form.reload()

    return Response({
        'status': 'success',
        'message': 'form updated successfully',
        'data': form.to_dict()
    }, status=HTTP_200_OK)


@api_view(['GET'])
@get_user_id
def list_forms(request, user_id):
    # TODO: we can paginate this route
    forms = []

    for form in Form.objects.filter(owner_id=user_id):
        forms.append(form.to_dict())
    
    if len(forms) == 0:
        return Response({
            'status': 'success',
            'message': 'no forms found',
            'data': None
        }, status=HTTP_204_NO_CONTENT)

    return Response({
        'status': 'success',
        'message': 'forms fetched successfully',
        'data': forms
    }, status=HTTP_200_OK)


@api_view(['GET'])
@get_user_id
@get_form_id
def list_submissions(request, user_id, form_id):
    # TODO: we can paginate this route
    try:
        form = Form.objects.get(id=form_id)
    except DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'form not found'
        }, status=HTTP_404_NOT_FOUND)
    else:
        if user_id != form.owner_id:
            return Response({
                'status': 'error',
                'message': 'only owner of the form can view the submissions'
            }, status=HTTP_403_FORBIDDEN)

    submissions = []

    for form_entry in FormEntry.objects.filter(user_id=user_id, form_id=form_id):
        submissions.append(form_entry.to_dict())
    
    if len(submissions) == 0:
        return Response({
            'status': 'success',
            'message': 'no submissions provided'
        }, status=HTTP_204_NO_CONTENT)

    return Response({
        'status': 'success',
        'message': 'submissions fetched successfully',
        'data': submissions
    }, status=HTTP_200_OK)


@api_view(['POST'])
@get_user_id
@get_form_id
def submit_form(request, user_id, form_id):
    try:
        form = Form.objects.get(id=form_id)
    except DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'form does not exist'
        }, status=HTTP_404_NOT_FOUND)
    
    try:
        form_entry = FormEntry.objects.get(user_id=user_id, form_id=form_id)
    except DoesNotExist:
        pass
    else:
        return Response({
            'status': 'error',
            'message': 'cannot re-submit a form'
        }, status=HTTP_400_BAD_REQUEST)

    submission = request.data

    if submission is None:
        return Response({
            'status': 'error',
            'message': 'missing submission data'
        }, status=HTTP_400_BAD_REQUEST)

    form_entry = FormEntry(user_id=user_id, form_id=form_id)
    answers = []
    mandatory_fields = []

    for field in form.fields:
        if field.mandatory:
            mandatory_fields.append(field.name)

    for field in submission:
        form_field_entry = FormFieldEntry(name=field, answer=submission[field])
        answers.append(form_field_entry)

        if field in mandatory_fields:
            mandatory_fields.remove(field)

    if len(mandatory_fields) != 0:
        return Response({
            'status': 'error',
            'message': 'required field(s) not filled',
            'data': mandatory_fields
        }, status=HTTP_400_BAD_REQUEST)

    form_entry.answers = answers
    form_entry.save()

    return Response({
        'status': 'success',
        'message': 'form submitted successfully'
    }, status=HTTP_200_OK)