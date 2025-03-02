from django.urls import path
from . import views  # Импортируем views из mongodb_check

urlpatterns = [
    path('', views.check_mongodb, name='check_mongodb'),  # Путь для проверки подключения
]
