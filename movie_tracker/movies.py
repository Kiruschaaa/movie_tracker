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
