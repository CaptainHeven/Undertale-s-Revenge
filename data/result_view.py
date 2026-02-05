import arcade
from pyglet.graphics import Batch
from .beautiful_button import BeautifulButton
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BACKGROUND_COLOR


class ResultView(arcade.View):
    def __init__(self, elapsed_time, victory, bullets_dodged=0, total_bullets=0, hp_remaining=0):
        super().__init__()
        self.elapsed_time = elapsed_time
        self.victory = victory
        self.bullets_dodged = bullets_dodged
        self.total_bullets = total_bullets
        self.hp_remaining = hp_remaining

        self.menu_button = None
        self.restart_button = None
        self.batch = None
        self.title_text = None
        self.time_text = None
        self.stats_text = None
        self.hp_text = None

    def setup(self):
        self.batch = Batch()

        # Кнопка возврата в меню
        self.menu_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4 - 50,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ВЫЙТИ В МЕНЮ"
        )
        self.menu_button.create_text_object(self.batch)

        # Кнопка рестарта
        self.restart_button = BeautifulButton(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 4 + 50,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "ИГРАТЬ СНОВА"
        )
        self.restart_button.create_text_object(self.batch)

        # Заголовок
        result_title = "ПОБЕДА!" if self.victory else "ПОРАЖЕНИЕ"
        title_color = arcade.color.GREEN if self.victory else arcade.color.RED

        self.title_text = arcade.Text(
            result_title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            title_color,
            48,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True,
            batch=self.batch
        )

        # Время выживания
        time_msg = f"Время: {self.elapsed_time:.1f} сек" if not self.victory else "Вы продержались 30 секунд!"
        self.time_text = arcade.Text(
            time_msg,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 60,
            arcade.color.WHITE,
            32,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

        # Статистика
        stats_msg = f"Уклонений: {self.bullets_dodged} / {self.total_bullets}"
        self.stats_text = arcade.Text(
            stats_msg,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 10,
            arcade.color.LIGHT_GRAY,
            28,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

        # Оставшееся HP
        hp_msg = f"Осталось HP: {self.hp_remaining}/92"
        self.hp_text = arcade.Text(
            hp_msg,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 40,
            arcade.color.YELLOW if self.hp_remaining > 46 else arcade.color.RED,
            24,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            batch=self.batch
        )

    def on_draw(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, BACKGROUND_COLOR)
        self.menu_button.draw()
        self.restart_button.draw()
        self.batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.menu_button:
            self.menu_button.check_hover(x, y)
        if self.restart_button:
            self.restart_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.menu_button and self.menu_button.check_click(x, y):
                from .main_menu_view import MainMenuView
                menu_view = MainMenuView()
                menu_view.setup()
                self.window.show_view(menu_view)
            elif self.restart_button and self.restart_button.check_click(x, y):
                from .game_view import GameView
                game_view = GameView()
                game_view.setup()
                self.window.show_view(game_view)