import unittest
from addevent import AddEvent


class TestWichDay(unittest.TestCase):
    def test_message_imput(self):
        class FakeMessage:

            def __init__(self, text):
                self.text = text
                self.from_user = {"id": 2066080793, "first_name": "Феникс", "is_bot": True}
                self.chat = {"first_name": "fakeuser", "id": 6565405695}

        fake_message = FakeMessage("some text")
        # Проверяем, что функция работает без ошибок при передаче объекта message
        self.assertIsNone(AddEvent.wich_day(fake_message))

    def test_user_input(self):
        # Создаем фейковый объект User
        class FakeUser:
            def __init__(self):
                self.id = 123  # Пример ID пользователя

        fake_user = FakeUser()

        # Проверяем, что функция работает без ошибок при передаче объекта User
        self.assertIsNone(AddEvent.wich_day(fake_user, common=False))


if __name__ == '__main__':
    unittest.main()
