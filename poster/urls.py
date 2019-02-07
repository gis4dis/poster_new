from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from apps.common.routers import CustomRouter
from apps.mc.api.urls import router as mc_router

# ===== MONITORING API PATTERNS =====
monitoring_patterns = (
    [
        url(r'pmo/', include('apps.processing.pmo.monitoring.urls')),
        url(r'o2/', include('apps.processing.o2.monitoring.urls')),
        url(r'ala/', include('apps.processing.ala.monitoring.urls')),
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
    path('', include('apps.mc.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('import/', include('apps.importing.urls')),

    # path('topics/drought/', include('apps.mc.urls')),
]

import debug_toolbar
urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns