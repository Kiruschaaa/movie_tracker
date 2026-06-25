import pytest
from unittest.mock import patch, call
from main import print_movies, menu


# ── print_movies ─────────────────────────────────────────────────
class TestPrintMovies:
    def test_empty_list_prints_empty_message(self, capsys):
        print_movies([])
        assert "Список пуст." in capsys.readouterr().out

    def test_one_movie_prints_table(self, capsys):
        print_movies([{"id": 1, "title": "Матрица", "year": 1999, "rating": 8.7, "genre": "фантастика"}])
        out = capsys.readouterr().out
        assert "Матрица" in out
        assert "1999" in out
        assert "фантастика" in out

    def test_multiple_movies_all_printed(self, capsys):
        movies = [
            {"id": 1, "title": "Матрица", "year": 1999, "rating": 8.7, "genre": "фантастика"},
            {"id": 2, "title": "Титаник", "year": 1997, "rating": 7.8, "genre": "мелодрама"},
        ]
        print_movies(movies)
        out = capsys.readouterr().out
        assert "Матрица" in out
        assert "Титаник" in out


# ── menu ─────────────────────────────────────────────────────────
class TestMenu:
    def _run_menu(self, inputs, db_path):
        """Хелпер: запускает menu() с заданными вводами и временной БД."""
        with patch("main.init_db") as mock_init, \
             patch("builtins.input", side_effect=inputs), \
             patch("main.get_all_movies", return_value=[]) as mock_all, \
             patch("main.add_movie") as mock_add, \
             patch("main.get_movie_by_id") as mock_get, \
             patch("main.update_movie") as mock_upd, \
             patch("main.delete_movie") as mock_del, \
             patch("main.filter_by_genre", return_value=[]) as mock_fg, \
             patch("main.filter_by_year", return_value=[]) as mock_fy:
            menu()
        return mock_init, mock_all, mock_add, mock_get, mock_upd, mock_del, mock_fg, mock_fy

    def test_exit_on_zero(self, capsys):
        with patch("main.init_db"), patch("builtins.input", side_effect=["0"]):
            menu()
        assert "Выход" in capsys.readouterr().out

    def test_show_all_movies(self):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["1", "0"]), \
             patch("main.get_all_movies", return_value=[]) as mock_all:
            menu()
        mock_all.assert_called()

    def test_add_movie_calls_add(self):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["2", "Матрица", "1999", "8.7", "фантастика", "0"]), \
             patch("main.add_movie") as mock_add:
            menu()
        mock_add.assert_called_once_with("Матрица", "1999", "8.7", "фантастика")

    def test_add_movie_value_error_shown(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["2", "", "1999", "8.7", "фантастика", "0"]), \
             patch("main.add_movie", side_effect=ValueError("Название не может быть пустым")):
            menu()
        assert "Ошибка" in capsys.readouterr().out

    def test_update_movie_not_found(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["3", "999", "0"]), \
             patch("main.get_movie_by_id", return_value=None):
            menu()
        assert "Фильм не найден" in capsys.readouterr().out

    def test_update_movie_invalid_id(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["3", "abc", "0"]):
            menu()
        assert "Некорректный ID" in capsys.readouterr().out

    def test_update_movie_calls_update(self):
        fake_movie = {"id": 1, "title": "Матрица", "year": 1999, "rating": 8.7, "genre": "фантастика"}
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["3", "1", "Новое", "", "", "", "0"]), \
             patch("main.get_movie_by_id", return_value=fake_movie), \
             patch("main.update_movie") as mock_upd:
            menu()
        mock_upd.assert_called_once_with(1, "Новое", None, None, None)

    def test_update_movie_value_error_shown(self, capsys):
        fake_movie = {"id": 1, "title": "Матрица", "year": 1999, "rating": 8.7, "genre": "фантастика"}
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["3", "1", "", "", "15", "", "0"]), \
             patch("main.get_movie_by_id", return_value=fake_movie), \
             patch("main.update_movie", side_effect=ValueError("Рейтинг должен быть от 0 до 10")):
            menu()
        assert "Ошибка" in capsys.readouterr().out

    def test_delete_movie_calls_delete(self):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["4", "1", "0"]), \
             patch("main.delete_movie") as mock_del:
            menu()
        mock_del.assert_called_once_with(1)

    def test_delete_movie_value_error_shown(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["4", "999", "0"]), \
             patch("main.delete_movie", side_effect=ValueError("не найден")):
            menu()
        assert "Ошибка" in capsys.readouterr().out

    def test_filter_by_genre_calls_filter(self):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["5", "фантастика", "0"]), \
             patch("main.filter_by_genre", return_value=[]) as mock_fg:
            menu()
        mock_fg.assert_called_once_with("фантастика")

    def test_filter_by_year_calls_filter(self):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["6", "1999", "0"]), \
             patch("main.filter_by_year", return_value=[]) as mock_fy:
            menu()
        mock_fy.assert_called_once_with("1999")

    def test_filter_by_year_value_error_shown(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["6", "abc", "0"]), \
             patch("main.filter_by_year", side_effect=ValueError("Год должен быть числом")):
            menu()
        assert "Ошибка" in capsys.readouterr().out

    def test_unknown_choice_shows_message(self, capsys):
        with patch("main.init_db"), \
             patch("builtins.input", side_effect=["9", "0"]):
            menu()
        assert "Неверный выбор" in capsys.readouterr().out
