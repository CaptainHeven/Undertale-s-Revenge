import arcade
from data.main_menu_view import MainMenuView
from data.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainMenuView()
    menu_view.setup()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()