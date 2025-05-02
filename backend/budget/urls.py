# backend/budget/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Імпортуємо ОБИДВА ViewSet'и
from .views import CategoryViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
# Додаємо реєстрацію для транзакцій
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]