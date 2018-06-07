from django.contrib import admin
from django.urls import path, include

from django.conf.urls import url
from rest_framework import routers
from apps.mc import views

router = routers.DefaultRouter()
router.register(r'properties', views.PropertyViewSet)

urlpatterns = [
    path('api/v1/timeseries/', views.TimeSeriesList.as_view()),
    url(r'^api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('import/', include('apps.importing.urls')),
]
