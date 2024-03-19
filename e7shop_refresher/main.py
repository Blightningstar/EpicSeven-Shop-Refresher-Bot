import os
import random
import time

import cv2
import numpy as np
import uiautomator2 as u2
from icecream import ic
from PIL import Image


class EpicSevenBot:
    def __init__(self):
        self.bookmark_image_path = ""
        self.bookmark_buy_confirmation = ""
        self.mystic_medal_image_path = ""
        self.mystic_medal_buy_confirmation = ""
        self.should_continue = True
        self.android_instance = None

    def load_resources(self):
        try:
            print("Loading the resources ...", end="\r")
            current_dir = os.path.dirname(os.path.abspath(__file__))

            self.bookmark_image_path = os.path.join(
                current_dir, "shop_products", "bookmark_shop_entry.png"
            )

            self.bookmark_buy_confirmation = os.path.join(
                current_dir, "shop_products", "bookmark_buy_confirmation.png"
            )

            self.mystic_medal_image_path = os.path.join(
                current_dir, "shop_products", "mystic_medal.png"
            )

            self.mystic_medal_image_path = os.path.join(
                current_dir, "shop_products", "mystic_medal_buy_confirmation.png"
            )

            print("Resources loaded successfully!")
        except Exception as e:
            print(f"There was an error loading the resources: {e}")

    def connect_to_android(self):
        try:
            # Connect to BlueStacks Emulator that has ADB enabled
            print("Connecting to Bluestack instance ...", end="\r")
            self.android_instance = u2.connect()
            bluestack_5 = self.android_instance.info

            if bluestack_5["currentPackageName"] != "com.stove.epic7.google":
                raise Exception(
                    "Epic Seven is not opened, please try again after opening the app."
                )

            print("Connected to BlueStacks successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to BlueStacks: {e}")
            return False

    def match_android_screen_to_image(self, search_image_path):
        try:
            # Capture a screenshot of the Android screen
            screenshot = self.android_instance.screenshot(format="opencv")
            # Load the image to search for
            image_to_search = cv2.imread(search_image_path)
            # Search for the presence of the image within the captured screenshot
            result = cv2.matchTemplate(
                screenshot, image_to_search, cv2.TM_CCOEFF_NORMED
            )
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # See if confidance range is 80% or higher
            if max_val > 0.8:
                x, y = max_loc  # Get the coordinates of the matched image
                h, w = image_to_search.shape[
                    :-1
                ]  # Get height and width of the matched image
                # Calculate lower right corner coordinates, to be able to click the buy button
                x2, y2 = x + w, y + h
                return True, x2, y2
            else:
                print("Resource not found")
                return False, 0, 0
        except Exception as e:
            print(f"There was an error: {e}")
            return False, 0, 0

    def buy_resource(self, x, y):
        # We open the resource buying confirmation menu
        self.android_instance.click(x, y)

        match_found, x, y = self.match_android_screen_to_image(
            self.bookmark_buy_confirmation
        )
        if match_found:
            self.android_instance.click(x, y)
        else:
            print("I am unable to see the buy confirmation!")

    def find_bookmarks(self):
        # Search for Bookmarks
        return self.match_android_screen_to_image(self.bookmark_image_path)

    def find_mystic_medals(self):
        # Search for Mystic Medals
        return self.match_android_screen_to_image(self.mystic_medal_image_path)

    def get_resources(self, bookmarks=True, mystic_medals=True):
        if bookmarks:
            # Search for Bookmarks
            result, x, y = self.find_bookmarks()
            if result:
                self.buy_resource(x, y)
        if mystic_medals:
            # Search for Mystic Medals
            result, x, y = self.find_mystic_medals()
            if result:
                self.buy_resource(x, y)

    def secret_shop_bot(self):
        while self.should_continue:
            self.get_resources()
            self.android_instance(scrollable=True).fling.vert.forward(steps=100)
            self.get_resources()
            self.should_continue = False

    def main(self):
        print("Starting the Epic 7 Secret Shop Refresher Bot ...")
        self.load_resources()
        time.sleep(3.0)
        self.should_continue = self.connect_to_android()
        self.secret_shop_bot()


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
    bot = EpicSevenBot()
    bot.main()
