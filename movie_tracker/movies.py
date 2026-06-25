import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "movies.db")


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            genre TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_movie(title, year, rating, genre, db_path=DB_PATH):
    title = title.strip()
    genre = genre.strip()
    if not title:
        raise ValueError("Название не может быть пустым")
    if not genre:
        raise ValueError("Жанр не может быть пустым")
    try:
        year = int(year)
    except (ValueError, TypeError):
        raise ValueError("Год должен быть числом")
    if year < 1888 or year > 2100:
        raise ValueError("Некорректный год")
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        raise ValueError("Рейтинг должен быть числом")
    if rating < 0 or rating > 10:
        raise ValueError("Рейтинг должен быть от 0 до 10")

    conn = get_connection(db_path)
    conn.execute(
        "INSERT INTO movies (title, year, rating, genre) VALUES (?, ?, ?, ?)",
        (title, year, rating, genre)
    )
    conn.commit()
    conn.close()


def get_all_movies(db_path=DB_PATH):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM movies ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_movie_by_id(movie_id, db_path=DB_PATH):
    conn = get_connection(db_path)
    row = conn.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def update_movie(movie_id, title=None, year=None, rating=None, genre=None, db_path=DB_PATH):
    movie = get_movie_by_id(movie_id, db_path)
    if movie is None:
        raise ValueError(f"Фильм с id={movie_id} не найден")

    if title is not None:
        title = title.strip()
        if not title:
            raise ValueError("Название не может быть пустым")
        movie["title"] = title

    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            raise ValueError("Год должен быть числом")
        if year < 1888 or year > 2100:
            raise ValueError("Некорректный год")
        movie["year"] = year

    if rating is not None:
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            raise ValueError("Рейтинг должен быть числом")
        if rating < 0 or rating > 10:
            raise ValueError("Рейтинг должен быть от 0 до 10")
        movie["rating"] = rating

    if genre is not None:
        genre = genre.strip()
        if not genre:
            raise ValueError("Жанр не может быть пустым")
        movie["genre"] = genre

    conn = get_connection(db_path)
    conn.execute(
        "UPDATE movies SET title=?, year=?, rating=?, genre=? WHERE id=?",
        (movie["title"], movie["year"], movie["rating"], movie["genre"], movie_id)
    )
    conn.commit()
    conn.close()


def delete_movie(movie_id, db_path=DB_PATH):
    movie = get_movie_by_id(movie_id, db_path)
    if movie is None:
        raise ValueError(f"Фильм с id={movie_id} не найден")
    conn = get_connection(db_path)
    conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()


def filter_by_genre(genre, db_path=DB_PATH):
    # SQLite LOWER() не работает с кириллицей — фильтруем в Python
    genre_lower = genre.strip().lower()
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM movies ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows if r["genre"].strip().lower() == genre_lower]


def filter_by_year(year, db_path=DB_PATH):
    try:
        year = int(year)
    except (ValueError, TypeError):
        raise ValueError("Год должен быть числом")
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM movies WHERE year = ? ORDER BY id", (year,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def print_movies(movies):
    if not movies:
        print("Список пуст.")
        return
    print(f"{'ID':<5} {'Название':<30} {'Год':<6} {'Рейтинг':<9} {'Жанр'}")
    print("-" * 60)
    for m in movies:
        print(f"{m['id']:<5} {m['title']:<30} {m['year']:<6} {m['rating']:<9} {m['genre']}")


def menu():
    init_db()
    while True:
        print("\n=== Трекер фильмов ===")
        print("1. Показать все фильмы")
        print("2. Добавить фильм")
        print("3. Обновить фильм")
        print("4. Удалить фильм")
        print("5. Фильтр по жанру")
        print("6. Фильтр по году")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            print_movies(get_all_movies())

        elif choice == "2":
            title = input("Название: ")
            year = input("Год: ")
            rating = input("Рейтинг (0-10): ")
            genre = input("Жанр: ")
            try:
                add_movie(title, year, rating, genre)
                print("Фильм добавлен.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "3":
            try:
                movie_id = int(input("ID фильма: "))
            except ValueError:
                print("Некорректный ID")
                continue
            movie = get_movie_by_id(movie_id)
            if not movie:
                print("Фильм не найден.")
                continue
            print(f"Текущие данные: {movie}")
            title = input("Новое название (Enter – оставить): ").strip() or None
            year_raw = input("Новый год (Enter – оставить): ").strip()
            year = year_raw if year_raw else None
            rating_raw = input("Новый рейтинг (Enter – оставить): ").strip()
            rating = rating_raw if rating_raw else None
            genre = input("Новый жанр (Enter – оставить): ").strip() or None
            try:
                update_movie(movie_id, title, year, rating, genre)
                print("Обновлено.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "4":
            try:
                movie_id = int(input("ID фильма: "))
                delete_movie(movie_id)
                print("Удалено.")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "5":
            genre = input("Жанр: ")
            print_movies(filter_by_genre(genre))

        elif choice == "6":
            year = input("Год: ")
            try:
                print_movies(filter_by_year(year))
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный выбор.")


if __name__ == "__main__":
    menu()
