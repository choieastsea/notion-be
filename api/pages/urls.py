from django.urls import path
from . import views
urlpatterns = [
    path('', views.PageAPIList.as_view()),
    path('<int:page_id>/', views.PageAPIDetail.as_view()),
]
