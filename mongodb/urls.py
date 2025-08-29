from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('mongo_connection/', views.mongo_connection, name='mongo_connection'),
    # path('mongo_login/', views.mongo_login, name='mongo_login'),
    # path('create_database/', views.create_database, name='create_database'),
    # path('welcome/', views.welcome, name='welcome'),
]