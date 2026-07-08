from django.urls import path
from . import views

app_name = "analyzer"

urlpatterns = [
    path("", views.home, name="home"),
    path("analyze/", views.analyze, name="analyze"),
    path("result/<int:pk>/", views.result, name="result"),
    path("history/", views.history, name="history"),
    path("api/analyze/", views.analyze_api, name="analyze_api"),
]
