import os
import random
import time

import keyboard
import win32api
from pyautogui import locateOnScreen, screenshot
from win32.lib import win32con


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


# sc = screenshot(region=(0,0,100,100))
# root_folder = os.getcwd()
# filename = "screenshot.png"
# sc.save(os.path.join(root_folder, filename))


def main():
    should_continue = True
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bookmark_image_path = os.path.join(current_dir, "shop_products", "bookmark.png")
    mystic_medal_image_path = os.path.join(
        current_dir, "shop_products", "mystic_medal.png"
    )
    while should_continue:
        try:
            position = locateOnScreen(
                bookmark_image_path, grayscale=True, confidence=0.7
            )
            if position is not None:
                print("I can see a bookmark")
                print(position)
                click(position.left + 40, position.top + 40)
        except Exception:
            print("I am unable to see a bookmark")

        try:
            position = locateOnScreen(
                mystic_medal_image_path, grayscale=True, confidence=0.7
            )
            if position is not None:
                print("I can see a Mystic Medal")
                print(position.left)
                print(position.top)
                click(position.left + 40, position.top + 40)
        except Exception:
            print("I am unable to see a Mystic Medal")

        should_continue = False


if __name__ == "__main__":
    # The shop should be open

    # The bot should register the amount of money & skystones available (Resources) and maybe ask the user how much should it use, but it definetly MUST stop once any of those resources are depleted or the amount inputed is reached.

    # The steps will be to:
    # - Check the first 2 items in the shop to see if they are bookmarks or medallions (Products)
    #     - If any of the first 2 items are a Product, we'll check our Resources and if available, we'll buy them
    # - Scroll the shop to see the remaining 4 items
    #     - If any of the remaining 4 items are a Product, we'll check our Resources and if available, we'll buy them
    # - We'll hit the Refresh Shop Button if skystones are available then we'll hit confirm
    # - The process continues until either we ran out of money or skystones or the program finishes.
    main()
