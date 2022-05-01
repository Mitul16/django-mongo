from django.urls import path

from .views import (
    create_form,
    get_form,
    delete_form,
    submit_form,
    update_form,
    list_forms,
    list_submissions,
)

urlpatterns = [
    path('create', create_form),
    path('list', list_forms),
    path('<str:form_id>', get_form),
    path('<str:form_id>/delete', delete_form),
    path('<str:form_id>/submissions', list_submissions),
    path('<str:form_id>/submit', submit_form),
    path('<str:form_id>/update', update_form),
]
