import csv
import arcade
from data.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, BACKGROUND_COLOR
from data.main_menu_view import MainMenuView


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Загружаем настройки из CSV (только яркость и звуки эффектов)
        try:
            with open('settings.csv', 'r', encoding='utf-8') as f:
                reader = list(csv.reader(f))
                data = reader[0]
                self.brightness = float(data[2])
                self.sounds_enabled = data[3].lower() == 'true'
        except:
            self.brightness = 1.0
            self.sounds_enabled = True

        # Флаг: загружена ли фоновая музыка
        self.music_loaded = False
        self.background_music = None

        # Загружаем музыку всегда (если файл есть)
        try:
            self.background_music = arcade.load_sound("materials/music.wav")
            if self.background_music:
                self.music_loaded = True
                # Всегда играем с громкостью 0.3
                self.background_music.play(volume=0.3, loop=True)
        except Exception as e:
            print(f"Не удалось загрузить фоновую музыку: {e}")
            self.music_loaded = False
            self.background_music = None

        # Применяем яркость
        brightness_factor = max(0.25, min(1.0, self.brightness))
        self.background_color = (
            int(BACKGROUND_COLOR[0] * brightness_factor),
            int(BACKGROUND_COLOR[1] * brightness_factor),
            int(BACKGROUND_COLOR[2] * brightness_factor),
            BACKGROUND_COLOR[3] if len(BACKGROUND_COLOR) > 3 else 255
        )

        self.darkness_factor = 1.0 - self.brightness

    def setup(self):
        menu_view = MainMenuView()
        menu_view.setup()
        self.show_view(menu_view)


def main():
    window = GameWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
