from enum import Enum
import pandas

from mongoengine import (
    Document,
    DynamicDocument,
    EmbeddedDocument
)
from mongoengine.document import DynamicEmbeddedDocument

from mongoengine.fields import (
    BooleanField,
    DynamicField,
    EmbeddedDocumentField,
    EnumField,
    ListField,
    ObjectIdField,
    StringField,
)

# Create your models here.

# TODO: We can add some additional attributes like:
# forms - created_at, last_updated_at
# submissions - submitted_at
# allow multiple submissions
# is_submission_open, is_submission_closed

class FormFieldType(Enum):
    TEXT = 'text'
    SINGLE_SELECT = 'single_select'
    NUMBER = 'number'
    DATE = 'date'


class FormField(EmbeddedDocument):
    name = StringField(max_length=255)
    type = EnumField(FormFieldType)
    options = ListField(StringField())
    mandatory = BooleanField()

    def to_dict(self):
        return {
            'name': self.name,
            'type': str(self.type),
            'options': self.options,
            'mandatory': self.mandatory
        }

    @staticmethod
    def from_dict(data):
        form_field = FormField()

        try:
            form_field.name = data['name']
            form_field.type = FormFieldType(data['type'])

            if form_field.type == FormFieldType.SINGLE_SELECT:
                options = data.get('options')

                # no `options` given
                if options is None or pandas.isna(options):
                    form_field.options = []
                # for CSV
                elif isinstance(options, str):
                    form_field.options = options.split(',')
                # for JSON
                elif isinstance(options, list):
                    form_field.options = options

            form_field.mandatory = data.get('mandatory', False)
        except (KeyError, ValueError):
            return None

        return form_field


class Form(Document):
    owner_id = ObjectIdField(required=True)
    name = StringField(max_length=255)
    fields = ListField(EmbeddedDocumentField(FormField))

    def to_dict(self):
        fields = []

        for field in self.fields:
            fields.append(field.to_dict())
        
        return {
            'owner_id': str(self.owner_id),
            'name': self.name,
            'fields': fields
        }


class FormFieldEntry(DynamicEmbeddedDocument):
    name = StringField(max_length=255)
    answer = DynamicField()

    def to_dict(self):
        return {
            'name': self.name,
            'answer': self.answer
        }


class FormEntry(DynamicDocument):
    user_id = ObjectIdField(required=True)
    form_id = ObjectIdField(required=True)
    answers = ListField(EmbeddedDocumentField(FormFieldEntry))

    def to_dict(self):
        answers = []

        for answer in self.answers:
            answers.append(answer.to_dict())
        
        return {
            'user_id': str(self.user_id),
            'form_id': str(self.form_id),
            'answers': answers
        }