import requests
import time


BASE_URL = "http://api:8084"

def test_create_todo():
    print("\n🔹 Тест: Создание задачи")
    todo_data = {
        "title": "Кушот",
        "description": "Торты"
    }
    response = requests.post(f"{BASE_URL}/todos/", json=todo_data)
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"
    data = response.json()
    print("✅ Задача создана:", data)
    return data["id"]


def test_get_todos():
    print("\n🔹 Тест: Получение списка задач")
    response = requests.get(f"{BASE_URL}/todos/")
    assert response.status_code == 200, f"Ошибка: {response.status_code}"
    todos = response.json()
    print(f"✅ Найдено задач: {len(todos)}")
    for todo in todos:
        print(f"  - [{todo['id']}] {todo['title']} (выполнено: {todo['completed']})")
    return todos


def test_update_todo(todo_id):
    print(f"\n🔹 Тест: Обновление задачи с ID={todo_id}")
    update_data = {
        "title": "Кушот",
        "description": "Теперь точно можно кушот торт",
        "completed": True
    }
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=update_data)
    assert response.status_code == 200, f"Ошибка: {response.status_code}, {response.text}"
    data = response.json()
    print("✅ Задача обновлена:", data)
    return data


def test_delete_todo(todo_id):
    print(f"\n🔹 Тест: Удаление задачи с ID={todo_id}")
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 204, f"Ошибка: {response.status_code}, {response.text}"
    print("✅ Задача удалена")


def test_long_task():
    print("\n🔹 Тест: Запуск длительной задачи")
    response = requests.post(f"{BASE_URL}/tasks/")
    assert response.status_code == 201, f"Ошибка: {response.status_code}, {response.text}"
    task = response.json()
    print("✅ Длительная задача запущена:", task)

    print("Ожидаем прогресс...")
    task_id = task["task_id"]

    for _ in range(5):  # Проверим прогресс 5 раз
        time.sleep(2)
        status_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"  Прогресс: {status['progress']}%, статус: {status['status']}")
            if status["status"] == "completed":
                print("✅ Задача завершена!")
                return
    print("⚠Задача ещё в процессе — продолжает выполняться.")


def run_tests():
    print("Запуск тестов API...")
    print(f"Подключение к: {BASE_URL}")

    try:
        # Проверка, запущен ли сервер
        health = requests.get(f"{BASE_URL}/")
        if health.status_code != 404:
            print("❌ Сервер не отвечает корректно")
            return
        print("✅ Сервер доступен")

        # Выполнение тестов
        todo_id = test_create_todo()
        test_get_todos()
        test_update_todo(todo_id)
        test_delete_todo(todo_id)

        # Тест длительной задачи
        test_long_task()

        print("\n Все тесты пройдены успешно!")

    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу. Убедитесь, что он запущен:")
        print("   python -m uvicorn main:app --reload")
    except AssertionError as e:
        print("❌ Тест провален:", e)
    except Exception as e:
        print("❌ Непредвиденная ошибка:", e)


if __name__ == "__main__":
    run_tests()