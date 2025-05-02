# backend/budget/views.py
from rest_framework import viewsets, permissions
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend # Для фільтрації
from rest_framework import filters

# Дозвіл, який перевіряє, чи об'єкт належить поточному користувачу
class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or view it.
    """
    def has_object_permission(self, request, view, obj):
        # Дозволяємо GET, HEAD, OPTIONS запити будь-кому (або можна обмежити авторизованими)
        # if request.method in permissions.SAFE_METHODS:
        #     return True
        # Дозвіл на запис/перегляд даємо тільки власнику об'єкта
        return obj.user == request.user

# ViewSet для Категорій
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated, IsOwner] # Тільки авторизовані користувачі, і тільки свої категорії
    permission_classes = [permissions.IsAuthenticated] # Поки що просто: тільки авторизовані користувачі

    def get_queryset(self):
        """
        Цей View має повертати список категорій тільки
        для поточного автентифікованого користувача.
        """
        user = self.request.user
        if user.is_authenticated:
            return Category.objects.filter(user=user)
        return Category.objects.none() # Або викликати помилку, якщо не автентифікований

    def perform_create(self, serializer):
        """
        При створенні нової категорії, автоматично встановлюємо поле 'user'
        на поточного автентифікованого користувача.
        """
        serializer.save(user=self.request.user)

    # Додаємо контекст запиту до серіалізатора для доступу до request.user у валідації
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


# Поки що залишимо ViewSet для Транзакцій пустим, додамо пізніше
class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows transactions to be viewed or edited.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated] # Тільки авторизовані
    # Додаємо можливість фільтрації, пошуку та сортування
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Поля, за якими можна фільтрувати (потрібно встановити django-filter: pip install django-filter)
    filterset_fields = ['category', 'transaction_type', 'transaction_date']
    # Поля, за якими можна шукати
    search_fields = ['description', 'category__name', 'amount']
    # Поля, за якими можна сортувати (за замовчуванням з моделі, але можна перевизначити)
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date'] # Сортування за замовчуванням

    def get_queryset(self):
        """
        Повертає список транзакцій тільки для поточного користувача.
        Також використовується для визначення queryset для PrimaryKeyRelatedField в серіалізаторі.
        """
        user = self.request.user
        if user.is_authenticated:
            # Додатково оптимізуємо запит, щоб уникнути N+1 проблеми при отриманні назви категорії
            return Transaction.objects.select_related('category').filter(user=user)
        return Transaction.objects.none()

    def perform_create(self, serializer):
        """
        При створенні транзакції автоматично встановлюємо користувача.
        """
        # Додатково можна тут перевірити баланс, якщо потрібно
        serializer.save(user=self.request.user)

    # Передаємо контекст запиту до серіалізатора
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    # Не забуваймо додати імпорт `DjangoFilterBackend` та `filters` зверху файлу!
    # Та встановити `django-filter