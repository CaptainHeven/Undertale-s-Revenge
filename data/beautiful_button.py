import arcade
from pyglet.graphics import Batch
from .constants import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR


class BeautifulButton:
    def __init__(self, center_x, center_y, width, height, text, font_size=26):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.is_hovered = False
        self.hover_animation = 0
        self.text_object = None

    def create_text_object(self, batch):
        self.text_object = arcade.Text(
            self.text,
            self.center_x,
            self.center_y,
            BUTTON_TEXT_COLOR,
            self.font_size,
            anchor_x="center",
            anchor_y="center",
            font_name="Arial",
            bold=True,
            batch=batch
        )

    def draw(self):
        if self.is_hovered:
            self.hover_animation = min(1.0, self.hover_animation + 0.1)
        else:
            self.hover_animation = max(0.0, self.hover_animation - 0.1)

        mix_amount = self.hover_animation
        r = int(BUTTON_COLOR[0] * (1 - mix_amount) + BUTTON_HOVER_COLOR[0] * mix_amount)
        g = int(BUTTON_COLOR[1] * (1 - mix_amount) + BUTTON_HOVER_COLOR[1] * mix_amount)
        b = int(BUTTON_COLOR[2] * (1 - mix_amount) + BUTTON_HOVER_COLOR[2] * mix_amount)
        current_color = (r, g, b)

        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, current_color)

        border_color = (180, 180, 220, 100 + int(100 * self.hover_animation))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, border_color, 2)

        if self.text_object:
            if self.is_hovered:
                self.text_object.color = (255, 255, 200)
            else:
                self.text_object.color = BUTTON_TEXT_COLOR

    def check_hover(self, x, y):
        self.is_hovered = (
                self.center_x - self.width / 2 < x < self.center_x + self.width / 2 and
                self.center_y - self.height / 2 < y < self.center_y + self.height / 2
        )
        return self.is_hovered

    def check_click(self, x, y):
        return self.check_hover(x, y)