from django.urls import include, path

urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/access/', include('access.urls')),
    path('api/business/', include('business.urls')),
]
