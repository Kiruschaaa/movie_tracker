# REPORT.md — Итоговый отчёт

**Проект:** Трекер фильмов  
**Тема:** Добавление фильмов (название, год, рейтинг, жанр), фильтрация по жанру или году  
**Язык:** Python 3, SQLite  
**Финальная версия:** 1.0.3

---

## 1. Путь по этапам

### Этап 1. Инициация и требования

Выбрал тему «трекер фильмов». Определил user stories:

- Как пользователь, я хочу добавлять фильм с названием, годом, рейтингом и жанром
- Как пользователь, я хочу просматривать весь список фильмов
- Как пользователь, я хочу редактировать данные фильма по ID
- Как пользователь, я хочу удалять фильм по ID
- Как пользователь, я хочу фильтровать фильмы по жанру
- Как пользователь, я хочу фильтровать фильмы по году

**MVP:** CRUD + два вида фильтрации, хранение в SQLite, консольный интерфейс.

Задачи оформлены в GitHub Issues, создана Kanban-доска с колонками: Backlog / In Progress / Review / Done.

### Этап 2. Проектирование

Структура данных — таблица `movies` с полями: id, title, year, rating, genre.

Схема взаимодействия:
```
пользователь → menu() → функции бизнес-логики → SQLite (movies.db)
```

Основные функции: `init_db`, `add_movie`, `get_all_movies`, `get_movie_by_id`, `update_movie`, `delete_movie`, `filter_by_genre`, `filter_by_year`.

### Этап 3. Разработка по TDD

Работал по циклу: написал тест → убедился что он падает → написал функцию → тест зелёный.

Порядок разработки:
1. `init_db`, `get_connection` — сервисные функции
2. `add_movie`, `get_all_movies`, `get_movie_by_id` — базовое чтение/запись
3. `update_movie`, `delete_movie` — обновление и удаление
4. `filter_by_genre`, `filter_by_year` — бизнес-логика фильтрации
5. `menu()` — консольный интерфейс в последнюю очередь

Каждую функцию оформлял через Pull Request.

Покрытие тестами бизнес-логики: **~85%** (не покрыт `menu()` — интерактивная консоль).  
Общее покрытие файла: **52%** (из-за большого объёма `menu()`).

### Этап 4. Приёмочное тестирование

Составил чек-лист на 15 пунктов (см. TEST_CHECKLIST.md).  
Прошёл вручную — нашёл 1 баг: фильтр по жанру не работал с кириллицей в разном регистре (SQLite LOWER() не поддерживает кириллицу). Написал тест, воспроизводящий баг, исправил фильтрацию, выпустил v1.0.1.

### Этап 5. Сопровождение

Получил 5 Issues от другой команды. Обработал все:
- **#3** (баг): фильтр по регистру — исправлен в v1.0.1
- **#4** (баг): рейтинг 0.0 вызывал ошибку — исправлен в v1.0.2
- **#5** (улучшение): сортировка по рейтингу в фильтрах — реализовано в v1.0.3
- **#6** (запрос на изменение): сделать год необязательным — отклонено, год является ключевым полем
- **#7** (вопрос): как запустить тесты — добавил инструкцию в README

Все ответы оставил в Issues и закрыл задачи.

---

## 2. Скриншот прогона тестов

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1
collected 32 items

tests/test_movies.py::TestInitDb::test_creates_table PASSED              [  3%]
tests/test_movies.py::TestAddMovie::test_add_valid_movie PASSED          [  6%]
tests/test_movies.py::TestAddMovie::test_add_multiple_movies PASSED      [  9%]
tests/test_movies.py::TestAddMovie::test_empty_title_raises PASSED       [ 12%]
tests/test_movies.py::TestAddMovie::test_whitespace_title_raises PASSED  [ 15%]
tests/test_movies.py::TestAddMovie::test_empty_genre_raises PASSED       [ 18%]
tests/test_movies.py::TestAddMovie::test_invalid_year_string_raises PASSED [ 21%]
tests/test_movies.py::TestAddMovie::test_year_too_old_raises PASSED      [ 25%]
tests/test_movies.py::TestAddMovie::test_year_too_far_raises PASSED      [ 28%]
tests/test_movies.py::TestAddMovie::test_invalid_rating_string_raises PASSED [ 31%]
tests/test_movies.py::TestAddMovie::test_rating_below_zero_raises PASSED [ 34%]
tests/test_movies.py::TestAddMovie::test_rating_above_ten_raises PASSED  [ 37%]
tests/test_movies.py::TestAddMovie::test_rating_boundary_zero PASSED     [ 40%]
tests/test_movies.py::TestAddMovie::test_rating_boundary_ten PASSED      [ 43%]
tests/test_movies.py::TestGetMovies::test_empty_db_returns_empty_list PASSED [ 46%]
tests/test_movies.py::TestGetMovies::test_get_by_id_found PASSED         [ 50%]
tests/test_movies.py::TestGetMovies::test_get_by_id_not_found PASSED     [ 53%]
tests/test_movies.py::TestUpdateMovie::test_update_title PASSED          [ 56%]
tests/test_movies.py::TestUpdateMovie::test_update_rating PASSED         [ 59%]
tests/test_movies.py::TestUpdateMovie::test_update_nonexistent_raises PASSED [ 62%]
tests/test_movies.py::TestUpdateMovie::test_update_with_empty_title_raises PASSED [ 65%]
tests/test_movies.py::TestUpdateMovie::test_update_with_bad_rating_raises PASSED [ 68%]
tests/test_movies.py::TestDeleteMovie::test_delete_existing PASSED       [ 71%]
tests/test_movies.py::TestDeleteMovie::test_delete_nonexistent_raises PASSED [ 75%]
tests/test_movies.py::TestDeleteMovie::test_delete_one_of_two PASSED     [ 78%]
tests/test_movies.py::TestFilterByGenre::test_filter_returns_correct PASSED [ 81%]
tests/test_movies.py::TestFilterByGenre::test_filter_case_insensitive PASSED [ 84%]
tests/test_movies.py::TestFilterByGenre::test_filter_no_match_returns_empty PASSED [ 87%]
tests/test_movies.py::TestFilterByYear::test_filter_returns_correct PASSED [ 90%]
tests/test_movies.py::TestFilterByYear::test_filter_invalid_year_raises PASSED [ 93%]
tests/test_movies.py::TestFilterByYear::test_filter_no_match_returns_empty PASSED [ 96%]
tests/test_movies.py::TestFilterByYear::test_filter_multiple_same_year PASSED [100%]

============================== 32 passed in 0.36s ==============================
```

---

## 3. Фрагмент журнала поддержки

| ID  | Тип        | Описание                                       | Решение                                      | Версия |
|-----|------------|------------------------------------------------|----------------------------------------------|--------|
| #3  | Баг        | Фильтр по жанру: регистр кириллицы             | Фильтрация перенесена в Python (.lower())     | 1.0.1  |
| #4  | Баг        | Рейтинг 0.0 вызывал ошибку валидации           | Исправлена проверка `if not rating`           | 1.0.2  |
| #5  | Улучшение  | Сортировка по рейтингу в результатах фильтрации | Добавлена сортировка по убыванию рейтинга    | 1.0.3  |

---

## 4. Ответы на вопросы

**Что было самым сложным в тестировании?**

Самым неожиданным оказался баг с SQLite и кириллицей — функция LOWER() в SQLite не работает с русскими буквами, и тест на регистронезависимость упал. Это было неочевидно: казалось бы, SQL — он везде SQL, но нет. Пришлось разобраться и переписать фильтрацию на Python. Также сложно было придумывать граничные случаи для валидации — первые несколько функций написал без тестов на границы, потом пришлось дописывать.

**Как изменилось бы приложение, если бы вы сразу знали обо всех багах?**

Я бы сразу сделал фильтрацию по жанру через Python, а не через SQL LOWER(). Также сразу бы написал тест на рейтинг = 0, потому что `if not value` — типичная ловушка в Python (0 это falsy). Скорее всего, архитектура не изменилась бы, просто было бы меньше итераций.

**Чему вы научились в процессе «поддержки»?**

Научился читать чужие баг-репорты и воспроизводить проблему по описанию. Понял, что сначала нужно написать тест, который ловит баг, и только потом чинить — так сразу видно, что фикс реально работает. Также понял, что некоторые запросы на изменение нужно уметь аргументированно отклонять (Issue #6 с необязательным годом).

---

## 5. Мини-ретроспектива

**Что удалось:**
- Написал 32 теста, покрывающих всю бизнес-логику
- Реально поймал баг через TDD (фильтр по регистру) — тест упал раньше, чем я успел заметить проблему вручную
- Документация получилась понятной
- Обработал все 5 Issues от другой команды

**Что можно улучшить:**
- Стоило с самого начала писать тесты на граничные значения (0, 10 для рейтинга), а не вспоминать о них на этапе поддержки
- Меню можно было вынести в отдельный файл `main.py`, чтобы покрытие тестами модуля `movies.py` было выше
- Можно было добавить поиск по части названия — было бы полезно, но в MVP не входило
