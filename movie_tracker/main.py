from movies import (
    init_db, add_movie, get_all_movies, get_movie_by_id,
    update_movie, delete_movie, filter_by_genre, filter_by_year
)


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
