from django.urls import path
from . import views

urlpatterns = [
    path('vehicle', views.search, name='search'),
]