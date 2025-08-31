from django.urls import path
from . import views

urlpatterns = [
    path('create-database/step1/', views.create_database_step1, name='create_database_step1'),
    path('create-database/step2/', views.create_database_step2, name='create_database_step2'),
    path('create-database/step3/', views.create_database_step3, name='create_database_step3'),
]
