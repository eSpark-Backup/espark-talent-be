from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import home

schema_url_patterns1 = [
    path('api/', include('eSparkTalentAPI.clienturls')),
]

schema_view1 = get_schema_view(
    openapi.Info(
        title="eSpark Talent APIs",
        default_version="v1",
        description="Client Dashboard APIs",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='http://54.162.147.127:8000/api/',
    patterns=schema_url_patterns1,
)

schema_url_patterns2 = [
    path('api/', include('eSparkTalentAPI.employeeurls')),
]

schema_view2 = get_schema_view(
    openapi.Info(
        title="eSpark Talent APIs",
        default_version="v1",
        description="Employee Dashboard APIs",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='http://54.162.147.127:8000/api/',
    patterns=schema_url_patterns2,
)

schema_url_patterns3 = [
    path('api/', include('eSparkTalentAPI.hrurls')),
]

schema_view3 = get_schema_view(
    openapi.Info(
        title="eSpark Talent APIs",
        default_version="v1",
        description="HR Dashboard APIs",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='http://54.162.147.127:8000/api/',
    patterns=schema_url_patterns3,
)

urlpatterns = [
    path('', home, name='home'),
    path("admin/", admin.site.urls),
    path("api/", include("eSparkTalentAPI.clienturls")),
    path("api/", include("eSparkTalentAPI.employeeurls")),
    path("api/", include("eSparkTalentAPI.hrurls")),
    path(
        "client_swagger/",
        schema_view1.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "employee_swagger/",
        schema_view2.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "hr_swagger/",
        schema_view3.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)