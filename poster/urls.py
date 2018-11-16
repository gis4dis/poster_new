from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.common.routers import CustomRouter
from apps.mc.api.urls import router as mc_router

# ===== MONITORING API PATTERNS =====
monitoring_patterns = (
    [
        url(r'pmo', include('apps.processing.pmo.monitoring.urls')),
    ]
    , 'monitoring')

# ===== BEGIN API PATTERNS =====
api_router = CustomRouter()
api_router.extend(mc_router)

api_patterns = ([url(r'^', include(api_router.urls)), ], 'api')

# ===== BEGIN URL PATTERNS =====
urlpatterns = []

# ===== INCLUDE API PATTERNS =====
urlpatterns += [
    path('api/v2/', include(api_patterns)),

    path('api/monitoring/', include(monitoring_patterns)),
]

# ===== INCLUDE STANDARD PATTERNS =====
urlpatterns += [
    path('', TemplateView.as_view(template_name="base_main.html")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('import/', include('apps.importing.urls')),

    path('map/', include('apps.mc.urls')),
]
