import os
import random
import time

import keyboard
import win32api
from pyautogui import screenshot
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

# while 1:
#     if pyautogui.locateOnScreen('bookmark.png', region=(150,175,350,600), grayscale=True, confidence=0.8) != None:
#         print("I can see a bookmark")
#         time.sleep(0.5)
#     else:
#         print("I am unable to see a bookmark")
#         time.sleep(0.5)


def main():
    print("Hello Main")


if __name__ == "__main__":
    # - Check the first 2 items in the shop to see if they are bookmarks or medallions (Products)
    #     - If any of the first 2 items are a Product, we'll check our Resources and if available, we'll buy them
    # - Scroll the shop to see the remaining 4 items
    #     - If any of the remaining 4 items are a Product, we'll check our Resources and if available, we'll buy them
    # - We'll hit the Refresh Shop Button if skystones are available then we'll hit confirm
    # - The process continues until either we ran out of money or skystones or the program finishes.
    main()
