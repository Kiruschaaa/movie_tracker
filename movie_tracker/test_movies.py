import pytest
import os
import tempfile
from movies import (
    init_db, add_movie, get_all_movies, get_movie_by_id,
    update_movie, delete_movie, filter_by_genre, filter_by_year
)


@pytest.fixture
def db(tmp_path):
    """Создаём временную БД для каждого теста."""
    db_path = str(tmp_path / "test_movies.db")
    init_db(db_path)
    return db_path


# ── Инициализация ────────────────────────────────────────────────
class TestInitDb:
    def test_creates_table(self, db):
        import sqlite3
        conn = sqlite3.connect(db)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        conn.close()
        assert any(t[0] == "movies" for t in tables)

    def test_init_idempotent(self, db):
        # Повторный вызов не ломает базу
        init_db(db)
        init_db(db)
        assert get_all_movies(db) == []


# ── Добавление ───────────────────────────────────────────────────
class TestAddMovie:
    def test_add_valid_movie(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        movies = get_all_movies(db)
        assert len(movies) == 1
        assert movies[0]["title"] == "Матрица"

    def test_add_multiple_movies(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Интерстеллар", 2014, 8.6, "фантастика", db)
        assert len(get_all_movies(db)) == 2

    def test_stored_fields_correct(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        m = get_all_movies(db)[0]
        assert m["year"] == 1999
        assert m["rating"] == 8.7
        assert m["genre"] == "фантастика"

    def test_title_stripped(self, db):
        add_movie("  Матрица  ", 1999, 8.7, "фантастика", db)
        assert get_all_movies(db)[0]["title"] == "Матрица"

    def test_empty_title_raises(self, db):
        with pytest.raises(ValueError, match="Название"):
            add_movie("", 2000, 7.0, "драма", db)

    def test_whitespace_title_raises(self, db):
        with pytest.raises(ValueError, match="Название"):
            add_movie("   ", 2000, 7.0, "драма", db)

    def test_empty_genre_raises(self, db):
        with pytest.raises(ValueError, match="Жанр"):
            add_movie("Фильм", 2000, 7.0, "", db)

    def test_invalid_year_string_raises(self, db):
        with pytest.raises(ValueError, match="Год"):
            add_movie("Фильм", "abc", 7.0, "драма", db)

    def test_year_none_raises(self, db):
        with pytest.raises(ValueError, match="Год"):
            add_movie("Фильм", None, 7.0, "драма", db)

    def test_year_too_old_raises(self, db):
        with pytest.raises(ValueError, match="Некорректный год"):
            add_movie("Фильм", 1800, 7.0, "драма", db)

    def test_year_too_far_raises(self, db):
        with pytest.raises(ValueError, match="Некорректный год"):
            add_movie("Фильм", 2200, 7.0, "драма", db)

    def test_year_boundary_min(self, db):
        add_movie("Первый фильм", 1888, 5.0, "документальный", db)
        assert get_all_movies(db)[0]["year"] == 1888

    def test_invalid_rating_string_raises(self, db):
        with pytest.raises(ValueError, match="Рейтинг"):
            add_movie("Фильм", 2000, "хорошо", "драма", db)

    def test_rating_none_raises(self, db):
        with pytest.raises(ValueError, match="Рейтинг"):
            add_movie("Фильм", 2000, None, "драма", db)

    def test_rating_below_zero_raises(self, db):
        with pytest.raises(ValueError, match="Рейтинг должен быть от 0 до 10"):
            add_movie("Фильм", 2000, -1, "драма", db)

    def test_rating_above_ten_raises(self, db):
        with pytest.raises(ValueError, match="Рейтинг должен быть от 0 до 10"):
            add_movie("Фильм", 2000, 11, "драма", db)

    def test_rating_boundary_zero(self, db):
        add_movie("Фильм0", 2000, 0, "драма", db)
        assert get_all_movies(db)[0]["rating"] == 0.0

    def test_rating_boundary_ten(self, db):
        add_movie("Фильм10", 2000, 10, "драма", db)
        assert get_all_movies(db)[0]["rating"] == 10.0


# ── Чтение ───────────────────────────────────────────────────────
class TestGetMovies:
    def test_empty_db_returns_empty_list(self, db):
        assert get_all_movies(db) == []

    def test_get_by_id_found(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        movie = get_movie_by_id(1, db)
        assert movie is not None
        assert movie["title"] == "Матрица"

    def test_get_by_id_not_found(self, db):
        assert get_movie_by_id(999, db) is None

    def test_movies_ordered_by_id(self, db):
        add_movie("Б", 2000, 7.0, "драма", db)
        add_movie("А", 1999, 8.0, "комедия", db)
        movies = get_all_movies(db)
        assert movies[0]["title"] == "Б"
        assert movies[1]["title"] == "А"


# ── Обновление ───────────────────────────────────────────────────
class TestUpdateMovie:
    def test_update_title(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, title="Матрица: Перезагрузка", db_path=db)
        assert get_movie_by_id(1, db)["title"] == "Матрица: Перезагрузка"

    def test_update_year(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, year=2003, db_path=db)
        assert get_movie_by_id(1, db)["year"] == 2003

    def test_update_rating(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, rating=9.0, db_path=db)
        assert get_movie_by_id(1, db)["rating"] == 9.0

    def test_update_genre(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, genre="боевик", db_path=db)
        assert get_movie_by_id(1, db)["genre"] == "боевик"

    def test_update_only_one_field_rest_unchanged(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, title="Новое", db_path=db)
        m = get_movie_by_id(1, db)
        assert m["year"] == 1999
        assert m["rating"] == 8.7
        assert m["genre"] == "фантастика"

    def test_update_nonexistent_raises(self, db):
        with pytest.raises(ValueError, match="не найден"):
            update_movie(999, title="Новое", db_path=db)

    def test_update_with_empty_title_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Название"):
            update_movie(1, title="", db_path=db)

    def test_update_with_empty_genre_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Жанр"):
            update_movie(1, genre="", db_path=db)

    def test_update_with_bad_year_string_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Год"):
            update_movie(1, year="abc", db_path=db)

    def test_update_with_bad_year_range_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Некорректный год"):
            update_movie(1, year=1700, db_path=db)

    def test_update_with_bad_rating_string_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Рейтинг"):
            update_movie(1, rating="хорошо", db_path=db)

    def test_update_with_bad_rating_raises(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        with pytest.raises(ValueError, match="Рейтинг"):
            update_movie(1, rating=15, db_path=db)

    def test_update_no_args_does_nothing(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        update_movie(1, db_path=db)
        m = get_movie_by_id(1, db)
        assert m["title"] == "Матрица"


# ── Удаление ─────────────────────────────────────────────────────
class TestDeleteMovie:
    def test_delete_existing(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        delete_movie(1, db)
        assert get_all_movies(db) == []

    def test_delete_nonexistent_raises(self, db):
        with pytest.raises(ValueError, match="не найден"):
            delete_movie(999, db)

    def test_delete_one_of_two(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Интерстеллар", 2014, 8.6, "фантастика", db)
        delete_movie(1, db)
        movies = get_all_movies(db)
        assert len(movies) == 1
        assert movies[0]["title"] == "Интерстеллар"


# ── Фильтрация по жанру ──────────────────────────────────────────
class TestFilterByGenre:
    def test_filter_returns_correct(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Титаник", 1997, 7.8, "мелодрама", db)
        result = filter_by_genre("фантастика", db)
        assert len(result) == 1
        assert result[0]["title"] == "Матрица"

    def test_filter_case_insensitive(self, db):
        # Баг #3: SQLite LOWER() не работает с кириллицей — фиксим в Python
        add_movie("Матрица", 1999, 8.7, "Фантастика", db)
        result = filter_by_genre("фантастика", db)
        assert len(result) == 1

    def test_filter_case_insensitive_upper(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        result = filter_by_genre("ФАНТАСТИКА", db)
        assert len(result) == 1

    def test_filter_no_match_returns_empty(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        assert filter_by_genre("комедия", db) == []

    def test_filter_genre_stripped(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        result = filter_by_genre("  фантастика  ", db)
        assert len(result) == 1

    def test_filter_multiple_same_genre(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Интерстеллар", 2014, 8.6, "фантастика", db)
        result = filter_by_genre("фантастика", db)
        assert len(result) == 2

    def test_filter_empty_db(self, db):
        assert filter_by_genre("фантастика", db) == []


# ── Фильтрация по году ───────────────────────────────────────────
class TestFilterByYear:
    def test_filter_returns_correct(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Титаник", 1997, 7.8, "мелодрама", db)
        result = filter_by_year(1999, db)
        assert len(result) == 1
        assert result[0]["title"] == "Матрица"

    def test_filter_invalid_year_raises(self, db):
        with pytest.raises(ValueError, match="Год"):
            filter_by_year("abc", db)

    def test_filter_no_match_returns_empty(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        assert filter_by_year(2000, db) == []

    def test_filter_multiple_same_year(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        add_movie("Бойцовский клуб", 1999, 8.8, "драма", db)
        result = filter_by_year(1999, db)
        assert len(result) == 2

    def test_filter_year_as_string_int(self, db):
        add_movie("Матрица", 1999, 8.7, "фантастика", db)
        result = filter_by_year("1999", db)
        assert len(result) == 1

    def test_filter_empty_db(self, db):
        assert filter_by_year(1999, db) == []
