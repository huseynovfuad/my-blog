from django.urls import path
from .views import add_or_delete_following

urlpatterns = [
    path('add-or-delete-follow/',add_or_delete_following,name='add-or-delete-follow'),
]
