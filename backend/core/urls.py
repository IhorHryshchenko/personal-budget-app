# backend/core/urls.py
from django.contrib import admin
from django.urls import path, include # Потрібно додати include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Підключаємо URL'и нашого додатку budget з префіксом 'api/budget/'
    path('api/budget/', include('budget.urls')),

    # Додамо URL'и для автентифікації DRF пізніше
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]