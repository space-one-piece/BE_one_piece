"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.analysis.views.scent_views import ScentDetailAPIView, ScentListCreateAPIView
from apps.question.views.results_views import ResultsCreateUrlAPIView
from apps.question.views.share_views import ShareOGView, ShareView
from apps.question.views.results_views import ShareCreateUrlAPIView, ShareViewAPIView

urlpatterns = [
    path("api/admin/", admin.site.urls),
    # web share
    path("api/v1/analyses/web-share", ShareCreateUrlAPIView.as_view(), name="web_share"),
    path("api/v1/analyses/web-share/<str:share_id>", ShareViewAPIView.as_view(), name="web_share"),
    # 유저 어드민
    path("api/v1/admin/", include(("apps.users.urls.admin-urls", "admin"))),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/share", ShareView.as_view(), name="share"),
    path("api/v1/<str:type>share-og/<int:results_id>", ShareOGView.as_view(), name="share-og"),
    # Redoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    path("api/v1/question/", include("apps.question.urls")),
    path("api/v1/chatbot/", include("apps.chatbot.urls")),
    path("api/v1/accounts/", include("apps.users.urls.urls")),
    # 이미지 분석
    path("api/v1/analyses", include("apps.analysis.urls.analysis_urls")),
    # 향 데이터
    path("api/v1/scents", ScentListCreateAPIView.as_view(), name="scent-list-create"),
    path("api/v1/scents/<int:id>", ScentDetailAPIView.as_view(), name="scent-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
