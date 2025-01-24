import sqlite3

def refresh_database(data):
    """Refreshes the database with the provided data."""
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()

    # Clear existing data (optional):
    cursor.execute("DELETE FROM themes")

    # Insert new data:
    cursor.executemany(
        "INSERT INTO themes (title, description, url) VALUES (:title, :description, :url)",
        data
    )

    conn.commit()
    conn.close()
    print("Database 'themes' table refreshed successfully.")

if __name__ == '__main__':
    # Example Data - you would load this from an external source/your forum:
    new_data = [
       {
            'title': 'Обсуждение новых технологий',
            'description': 'Обсуждаем последние достижения в области науки и технологий.',
            'url': 'forum/topic/1'
        },
        {
            'title': 'Советы по изучению программирования',
            'description': 'Делимся советами и ресурсами для изучения языков программирования.',
            'url': 'forum/topic/2'
        },
       {
            'title': 'Вопросы по дизайну сайтов',
            'description': 'Задаем вопросы и делимся опытом в веб дизайне',
            'url': 'forum/topic/3'
        },
         {
            'title': 'Тема про кулинарию',
            'description': 'Рецепты и советы от профессионалов',
            'url': '/topic/4'
        },
         {
            'title': 'Тема про путешествия',
            'description': 'Советы и места для посещения',
            'url': '/topic/5'
        },
       ]
    refresh_database(new_data)