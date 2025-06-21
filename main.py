# main.py
from backend import Backend
from frontend_pygame import PygameFrontend

if __name__ == "__main__":
    # 1. Создаем экземпляр игровой логики
    game_backend = Backend()

    # 2. Создаем экземпляр визуализатора, передавая ему бекэнд
    game_frontend = PygameFrontend(game_backend)

    # 3. Запускаем главный цикл визуализатора
    game_frontend.run()
