from django.urls import path

from .views import (
    login,
    logout,
    signup
)

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('signup', signup),
]
