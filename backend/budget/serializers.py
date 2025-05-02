# backend/budget/serializers.py
from rest_framework import serializers
from .models import Category, Transaction
from django.contrib.auth.models import User
import datetime

class CategorySerializer(serializers.ModelSerializer):
    # Додаємо поле user, але робимо його read_only=True при отриманні даних,
    # бо користувач буде визначатися автоматично при створенні категорії.
    # StringRelatedField показує ім'я користувача замість ID.
    user = serializers.StringRelatedField(read_only=True)
    # Можна додати поле для передачі user_id при створенні,
    # але краще ми його встановимо у View автоматично.

    class Meta:
        model = Category
        # Вказуємо поля, які будуть включені в JSON
        # 'id' додається автоматично, 'created_at', 'updated_at' поки не включаємо
        fields = ['id', 'name', 'type', 'user']
        read_only_fields = ['user'] # Ми встановимо користувача у View

    # Валідація на рівні серіалізатора (додатково до унікальності в моделі)
    def validate_name(self, value):
        # Перевіряємо, чи у поточного користувача вже є категорія з такою назвою
        user = self.context['request'].user # Отримуємо користувача з контексту запиту
        if Category.objects.filter(user=user, name__iexact=value).exists():
             # Якщо ми оновлюємо існуючу категорію, треба дозволити зберегти ту саму назву
            if self.instance is None or self.instance.name.lower() != value.lower():
                 raise serializers.ValidationError("Категорія з такою назвою вже існує.")
        return value

# Поки що залишимо серіалізатор для Транзакцій пустим, додамо пізніше
class TransactionSerializer(serializers.ModelSerializer):
    # Показуємо ім'я користувача і назву категорії замість ID
    user = serializers.StringRelatedField(read_only=True)
    # Щоб показувати ім'я категорії, але дозволяти передавати ID при створенні/оновленні
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Ми будемо передавати category ID при створенні/оновленні
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(), # Початково порожній, змінимо у View
        allow_null=True, # Дозволяємо транзакції без категорії
        required=False   # Робимо категорію не обов'язковою
    )

    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'amount',
            'transaction_type',
            'transaction_date',
            'description',
            'category',         # ID категорії для записів POST/PUT
            'category_name',    # Ім'я категорії для читання (GET)
            'created_at',       # Може бути корисним на фронті
            'updated_at',
        ]
        read_only_fields = ['user', 'category_name', 'created_at', 'updated_at']

    def validate_category(self, value):
        """
        Перевіряє, чи існує категорія і чи належить вона поточному користувачу.
        """
        user = self.context['request'].user
        if value and not Category.objects.filter(user=user, id=value.id).exists():
            raise serializers.ValidationError("Вибрана категорія не існує або не належить вам.")
        return value

    def validate(self, data):
        """
        Перевіряє узгодженість типу транзакції та типу вибраної категорії.
        Викликається після індивідуальних валідацій полів.
        """
        category = data.get('category')
        transaction_type = data.get('transaction_type')

        # Якщо категорія вибрана і тип транзакції визначений
        if category and transaction_type:
            if category.type != transaction_type:
                 raise serializers.ValidationError(
                     f"Тип транзакції '{transaction_type}' не відповідає типу категорії '{category.name}' ({category.type})."
                 )

        return data

    # Перевизначаємо __init__, щоб динамічно встановити queryset для поля category
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Якщо серіалізатор використовується у контексті запиту (тобто через View)
        if 'request' in self.context:
            user = self.context['request'].user
            # Дозволяємо вибирати тільки категорії поточного користувача
            self.fields['category'].queryset = Category.objects.filter(user=user)
        else:
             # Якщо контексту немає (напр. при прямому створенні серіалізатора),
             # залишаємо queryset порожнім або загальним (менш безпечно)
             # self.fields['category'].queryset = Category.objects.all() # обережно!
             pass