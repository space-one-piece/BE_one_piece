from django.urls import path

from ..views.scent_views import ScentDetailAPIView, ScentListCreateAPIView

app_name = "scent_management"

urlpatterns = [
    path("", ScentListCreateAPIView.as_view(), name="scent-list-create"),
    path("/<int:id>", ScentDetailAPIView.as_view(), name="scent-detail"),
]
