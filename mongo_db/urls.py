from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save-mongo-config/', views.save_mongo_config, name='save_mongo_config'),
    path('login/', views.login, name='login'),
]
