from django.contrib import admin
from .models import Category, Transaction # Імпортуємо наші моделі

# Налаштування відображення Категорій в адмінці
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'type', 'created_at') # Які поля показувати у списку
    list_filter = ('user', 'type') # Фільтри справа
    search_fields = ('name',) # Поле для пошуку

# Налаштування відображення Транзакцій в адмінці
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'category', 'transaction_date', 'description')
    list_filter = ('user', 'transaction_type', 'category', 'transaction_date')
    search_fields = ('description', 'category__name') # Шукати по опису та назві категорії
    list_editable = ('amount', 'category', 'description', 'transaction_date') # Можливість редагувати прямо у списку
    date_hierarchy = 'transaction_date' # Навігація по даті зверху