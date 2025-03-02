from django.urls import path, include
#
from home.views import home



urlpatterns = [
    path('', home, name='home'),
    path('check-mongodb/', include('check_mongodb.urls')),
]
