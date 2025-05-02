# backend/budget/serializers.py
from rest_framework import serializers
from .models import Category, Transaction
from django.contrib.auth.models import User

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
     pass # Додамо код сюди пізніше