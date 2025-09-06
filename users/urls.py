from django.urls import path
from . import views

app_name = 'users'  # Add namespace for better URL organization

urlpatterns = [
    path('create-admin/step1/', views.create_admin_step1, name='create_admin_step1'),
    path('create-admin/step2/', views.create_admin_step2, name='create_admin_step2'),
    path('create-admin/step3/', views.create_admin_step3, name='create_admin_step3'),
]