# backend/budget/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet # Імпортуємо наш ViewSet

# Створюємо роутер DRF
router = DefaultRouter()
# Реєструємо ViewSet для категорій. DRF автоматично створить URL'и:
# /api/budget/categories/ - для списку (GET) та створення (POST)
# /api/budget/categories/{id}/ - для отримання (GET), оновлення (PUT/PATCH), видалення (DELETE)
router.register(r'categories', CategoryViewSet, basename='category')
# router.register(r'transactions', TransactionViewSet, basename='transaction') # Додамо пізніше

urlpatterns = [
    # Включаємо URL'и, згенеровані роутером
    path('', include(router.urls)),
]