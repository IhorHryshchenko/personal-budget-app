from django.db import models
from django.contrib.auth.models import User # Імпортуємо стандартну модель User
from django.utils import timezone # Для transaction_date

# Абстрактна модель для відстеження часу створення/оновлення
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # Вказуємо, що це абстрактна модель

# Модель Категорії
class Category(BaseModel):
    class CategoryType(models.TextChoices):
        INCOME = 'INCOME', 'Дохід'
        EXPENSE = 'EXPENSE', 'Витрата'

    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    type = models.CharField(
        max_length=7,
        choices=CategoryType.choices,
        default=CategoryType.EXPENSE,
        verbose_name="Тип категорії"
    )
    # Зв'язок з користувачем. related_name дозволяє звертатися user.categories
    # on_delete=models.CASCADE означає, що при видаленні користувача видаляться і його категорії
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', verbose_name="Користувач")

    class Meta:
        verbose_name = "Категорія" # Як модель буде називатися в адмінці (однина)
        verbose_name_plural = "Категорії" # Те саме, множина
        unique_together = ('user', 'name') # Назва категорії має бути унікальною для кожного користувача

    def __str__(self):
        # Як об'єкт категорії буде представлятися у вигляді рядка (напр., в адмінці)
        return f"{self.name} ({self.get_type_display()}) - {self.user.username}"


# Модель Транзакції
class Transaction(BaseModel):
    class TransactionType(models.TextChoices):
        INCOME = 'INCOME', 'Дохід'
        EXPENSE = 'EXPENSE', 'Витрата'

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума")
    transaction_type = models.CharField(
        max_length=7,
        choices=TransactionType.choices,
        verbose_name="Тип транзакції"
    )
    # default=timezone.now дозволяє встановити поточну дату за замовчуванням у формі
    transaction_date = models.DateField(default=timezone.now, verbose_name="Дата транзакції")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Опис")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name="Користувач")
    # null=True, blank=True дозволяють мати транзакції без категорії (напр., початковий баланс)
    # on_delete=models.SET_NULL: якщо категорію видалять, поле category у транзакції стане NULL
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name="Категорія"
    )

    class Meta:
        verbose_name = "Транзакція"
        verbose_name_plural = "Транзакції"
        ordering = ['-transaction_date', '-created_at'] # Сортування за замовчуванням: спочатку новіші

    def __str__(self):
        category_name = self.category.name if self.category else "Без категорії"
        return f"{self.get_transaction_type_display()}: {self.amount} ({category_name}) on {self.transaction_date}"

    # Додаткова перевірка при збереженні (важливо!)
    def save(self, *args, **kwargs):
        # Переконуємось, що тип транзакції відповідає типу категорії
        if self.category and self.category.type != self.transaction_type:
            raise ValueError(f"Тип транзакції ({self.transaction_type}) не відповідає типу категорії ({self.category.type})")
        super().save(*args, **kwargs) # Викликаємо стандартний метод save

# Можна додати модель BudgetLimit пізніше, якщо потрібно буде реалізовувати цю функцію
# class BudgetLimit(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='limits')
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='limits')
#     limit_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     # Додати поля для періоду (місяць, рік), дати початку/кінця
#     # ...