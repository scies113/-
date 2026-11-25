# Система учета домашних заготовок

Проект ведёт каталог сырья и рецептов, показывает партии банок и остатки в погребе. Веб-интерфейс использует Python 3.10+, Django 5.2, Django ORM, SQLite и шаблоны Django с Bootstrap. Консольное приложение из ПР1–ПР3 хранит данные в JSON и запускается отдельно.

Автор — Золотов Максим Денисович, ЭФБО-12-24.

## Запуск веб-приложения

```powershell
git clone https://github.com/scies113/-.git home_preserves
cd home_preserves
git switch pr9-django-orm
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py import_pr7
python manage.py runserver
```

Откройте [главную страницу](http://127.0.0.1:8000/). На Linux и macOS окружение активируется командой `source venv/bin/activate`.

## База данных и перенос из ПР7

Django создаёт таблицы в локальном файле `db.sqlite3`. Миграции лежат в `preserves/migrations/` и `batches/migrations/`. По умолчанию команда `import_pr7` читает исходный файл `data/preserves.sqlite` в режиме только для чтения. Чтобы загрузить другую копию базы ПР7, передайте её путь:

```powershell
python manage.py import_pr7 "C:\путь\к\preserves.sqlite"
```

Импорт переносит записи в порядке «сырьё → заготовки → партии» с сохранением ID, внешних ключей, дат, количества и статусов. Повторный запуск пропускает совпадающие записи. При конфликте ID с изменённой записью или нарушении ограничений импорт откатывается целиком. Для запуска с пустым каталогом достаточно применить миграции.

| Модель | Поля помимо ID | Связь |
| --- | --- | --- |
| `Product` | `name`, `category` | `product.preserves` возвращает рецепты |
| `Preserve` | `name`, `product`, `recipe_notes` | `ForeignKey` на `Product`; `preserve.batches` возвращает партии |
| `Batch` | `preserve`, `production_date`, `quantity`, `is_consumed` | `ForeignKey` на `Preserve` |

Для первичных ключей используется `BigAutoField`. У обеих связей задано `on_delete=RESTRICT`. Количество банок неотрицательное, партия по умолчанию активна, примечания к рецепту могут быть пустыми.

## Страницы

| Маршрут | Назначение |
| --- | --- |
| `/` | Сводка по сырью, рецептам и остаткам, три партии с наибольшим запасом |
| `/preserves/` | Каталог с поиском по названию заготовки |
| `/preserves/<id>/` | Карточка заготовки со сведениями о сырье |
| `/preserves/products/` | Справочник сырья с количеством рецептов |
| `/batches/` | Активные партии, по пять на страницу |
| `/batches/<id>/` | Карточка партии и ссылка на её рецепт |
| `/batches/search/` | Поиск по названию заготовки или сырья, фильтры по дате, статусу и категории, сортировка и пагинация |
| `/batches/statistics/` | Количество партий, остатки банок и группировка по заготовкам |

Поиск по названиям учитывает русский регистр через нормализацию Unicode. Параметры поиска партий можно комбинировать. Например, `/batches/search/?date=2026-10-22&status=active&sort=quantity` показывает активные партии на указанную дату по убыванию количества. Ссылки пагинации сохраняют параметры. Недопустимые дата, статус и категория показывают сообщение об ошибке. Неизвестный режим сортировки заменяется сортировкой по дате от новых партий.

### Где посмотреть ORM-запросы

- `homepage/views.py` считает рецепты и продукты, суммирует активные остатки и ограничивает выдачу трёх крупнейших партий срезом.
- `preserves/views.py` сортирует каталог по названию, выполняет поиск по одному полю, получает карточку через `get()` и аннотирует продукты числом рецептов через `Count()`.
- `batches/views.py` исключает израсходованные партии через `exclude()` и загружает связанные объекты для карточки через `select_related()`. Поиск получает категории через `values_list().distinct()`, применяет `filter()` по одному или нескольким условиям, ищет по двум полям через `Q` и выбирает нужные поля через `values()`. Статистика использует `aggregate()` и `annotate()`. Заготовки без партий отображаются с нулевыми значениями.

### Проверка CRUD в Django shell

Команды создают и удаляют отдельную учебную запись.

```python
# python manage.py shell
from preserves.models import Product

demo = Product.objects.create(name="Пробная запись", category="овощи")
Product.objects.get(pk=demo.pk).name
demo.name = "Обновлённая пробная запись"
demo.save(update_fields=["name"])
demo.refresh_from_db()
demo.name
demo.delete()
```

## Структура проекта

- `config/` содержит настройки и корневые маршруты Django.
- `homepage/`, `preserves/` и `batches/` содержат представления, маршруты и шаблоны. Модели размещены в приложениях `preserves` и `batches`.
- `preserves/management/commands/import_pr7.py` читает исходную базу и записывает данные через ORM.
- `templates/` и `static/` содержат общие шаблоны, стили и скрипты.
- `main.py`, `models/`, `storage.py` и `data/*.json` обслуживают консольную версию. Запуск — `python main.py`.
- `db/` и `sql/` содержат материалы ПР7 и прежний скрипт импорта JSON в исходную базу.

## Проверки

```powershell
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check --dry-run
python -m pytest -v
python -m flake8 . --extend-exclude=venv
```
