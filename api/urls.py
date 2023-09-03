from django.urls import path, include

urlpatterns = [
    path('page/', include('api.pages.urls')),
]
