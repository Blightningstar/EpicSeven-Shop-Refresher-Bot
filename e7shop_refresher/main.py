import os
import random
import time

import cv2
import numpy as np
import pytesseract
import uiautomator2 as u2
from icecream import ic
from PIL import Image


class EpicSevenBot:
    def __init__(self):

        # All the variables for images paths
        self.bookmark_image_path = ""
        self.bookmark_buy_confirmation = ""
        self.mystic_medal_image_path = ""
        self.mystic_medal_buy_confirmation = ""
        self.refresh_store_button = ""
        self.refresh_store_confirmation = ""
        self.no_skystones_left = ""
        self.in_secret_shop = ""
        self.own_gold = ""

        # All configuration values for the bot to work
        self.should_continue = True
        self.android_instance = None
        self.android_port = 8000
        self.android_port_txt_path = "android_ADB_port.txt"
        self.buy_bookmarks = True
        self.buy_mystic_medals = True
        self.amount_skystones_to_spent = None
        self.amount_coins_to_spent = None

    def show_shopping_report(self):
        """
        This method prints all the shopping statistics.
        """
        pass

    def load_image_resources(self):
        """
        This method loads all the images required for the script
        to match on the android instance during runtime.
        """
        try:
            print("Loading the image resources ...", end="\r")
            current_dir = os.path.dirname(os.path.abspath(__file__))

            self.bookmark_image_path = os.path.join(
                current_dir, "shop_products", "bookmark_shop_entry.png"
            )

            self.bookmark_buy_confirmation = os.path.join(
                current_dir, "shop_products", "bookmark_buy_confirmation.png"
            )

            self.mystic_medal_image_path = os.path.join(
                current_dir, "shop_products", "mystic_medal_shop_entry.png"
            )

            self.mystic_medal_buy_confirmation = os.path.join(
                current_dir, "shop_products", "mystic_medal_buy_confirmation.png"
            )

            self.refresh_store_button = os.path.join(
                current_dir, "shop_products", "refresh_button.png"
            )

            self.refresh_store_confirmation = os.path.join(
                current_dir, "shop_products", "refresh_store_confirmation.png"
            )

            self.no_skystones_left = os.path.join(
                current_dir, "shop_products", "no_skystones_left.png"
            )

            self.in_secret_shop = os.path.join(
                current_dir, "shop_products", "secret_shop.png"
            )

            self.own_gold = os.path.join(current_dir, "shop_products", "own_gold.png")

            print("Image resources loaded successfully!")
        except Exception as e:
            print(f"There was an error loading the resources: {e}")
            self.should_continue = False

    def connect_to_android(self):
        """
        This method handles the connection of the script to android instance.
        """
        try:
            # Connect to BlueStacks Emulator that has ADB enabled
            print("Connecting to Bluestack instance ...", end="\r")
            self.android_instance = u2.connect(f"127.0.0.1:{self.android_port}")
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

    def extract_numbers_from_image(self, image_path):
        """
        This method reads the screen next to an image and returns the text read.
        """
        img = Image.open(image_path)
        numbers = pytesseract.image_to_string(img)
        return numbers

    def match_android_screen_to_image(self, search_image_path):
        """
        This method matches the image at search_image_path and finds it in the E7 screen.
        """
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
                print(f"Resource at {search_image_path} not found on screen.")
                return False, 0, 0
        except Exception as e:
            print(f"There was an error: {e}")
            return False, 0, 0

    def buy_resource(self, x, y):
        """
        This method handles the logic for buying bookmarks and mystic medals.
        """
        # We open the resource buying confirmation menu
        self.android_instance.click(x, y)

        match_found, x, y = self.match_android_screen_to_image(
            self.bookmark_buy_confirmation
        )
        if match_found:
            self.android_instance.click(x, y)
        else:
            print("I am unable to see the buy confirmation!")

    def check_skystones_and_coins(self):
        """
        This method checks if spending limit has been reached for Skystones or Coins.
        """
        match_found, _, _ = self.match_android_screen_to_image(self.own_gold)
        if not match_found:
            print("weird")
        else:
            print("Good")

    def get_resources(self):
        """
        This method handles the logic for searching/buying bookmarks and mystic medals.
        """
        if self.buy_bookmarks:
            # Search for Bookmarks
            result, x, y = self.match_android_screen_to_image(self.bookmark_image_path)
            if result:
                self.check_skystones_and_coins()
                self.buy_resource(x, y)
        if self.buy_mystic_medals:
            # Search for Mystic Medals
            result, x, y = self.match_android_screen_to_image(
                self.mystic_medal_image_path
            )
            if result:
                self.check_skystones_and_coins()
                self.buy_resource(x, y)

    def refresh_store(self):
        """
        This method handles the logic for refreshing the store.
        """
        match_found, x, y = self.match_android_screen_to_image(
            self.refresh_store_button
        )
        if not match_found:
            print("I am unable to see the refresh button!")
        else:
            self.android_instance.click(x, y)
            time.sleep(0.3)
            match_found, x, y = self.match_android_screen_to_image(
                self.refresh_store_confirmation
            )
            if not match_found:
                print("I am unable to see the refresh confirmation pop up!")
            else:
                self.android_instance.click(x, y)
                time.sleep(0.3)
                match_found, x, y = self.match_android_screen_to_image(
                    self.no_skystones_left
                )
                if match_found:
                    print("You're out of Skystones!")
                    self.should_continue = False

    def check_if_inside_secret_shop(self):
        """
        This method stops execution of the script if the E7 game is not inside Garo's Secret Shop.
        """
        match_found, _, _ = self.match_android_screen_to_image(self.in_secret_shop)
        if not match_found:
            print("This bot only works inside the tabern's secret shop!")
            self.should_continue = False
        else:
            print("Hi Garo, I'll be ordering the usual!")

    def secret_shop_bot(self):
        """
        This method contains the logic for matching, clicking, buying and refreshing the shop.
        """
        while self.should_continue:
            self.get_resources()
            self.android_instance.swipe(1230, 820, 1229, 480, 0.1)
            self.get_resources()
            self.refresh_store()
        self.show_shopping_report()
        print("The Epic 7 Secret Shop Refresher Bot run has finished. Bye!")

    def get_user_input(
        self,
        prompt,
        prompt_options=None,
        prompt_option_values=None,
        default_input=None,
        default_value=None,
    ):
        """
        This method handles user inputs for an amazing and smooth UX.
        """
        incorrect_input = True
        while incorrect_input:
            user_input = input(prompt).lower()
            # User pressed enter and choose the default value
            if (
                user_input == ""
                and default_input is not None
                and default_value is not None
            ):
                incorrect_input = False
                return default_value
            if prompt_options:
                # User inputted one of the prompt_options
                if user_input in prompt_options:
                    incorrect_input = False
                    if prompt_option_values:
                        return prompt_option_values[prompt_options.index(user_input)]
                    else:
                        return user_input
            else:
                incorrect_input = False
                return user_input

    def check_stored_android_port(self):
        """
        This method allows to handle preserving the ADB_port variable throughout different script runs.
        """
        port_found = False
        if os.path.exists(self.android_port_txt_path):
            with open(self.android_port_txt_path, "r") as file:
                first_line = file.readline().strip()
                if first_line.startswith("ADB_port="):
                    self.android_port = first_line.split("=")[1]
                    port_found = True
                    print("Stored ADB Port found: ", self.android_port)
        if not os.path.exists(self.android_port_txt_path) or not port_found:
            with open(self.android_port_txt_path, "w") as file:
                should_store_ADB_port = self.get_user_input(
                    prompt="I see you do not have your ADB port stored yet. You want to store it? (y/n) [y]:  ",
                    prompt_options=["y", "n"],
                    prompt_option_values=[True, False],
                    default_input="y",
                    default_value=True,
                )
                self.android_port = self.get_user_input(
                    prompt="In which port is your Android instance ADB running?:  ",
                )
                if should_store_ADB_port:
                    file.write(f"ADB_port={self.android_port}\n")
                    print("ADB Port Stored!")

    def get_initial_user_configuration_info(self):
        """
        This method allows the user to go through the configuration menu for the
        script runtime decisions returning its position on the android screen.
        """
        self.check_stored_android_port()
        self.buy_bookmarks = self.get_user_input(
            prompt="Do you want to buy Bookmarks? (y/n) [y]:  ",
            prompt_options=["y", "n"],
            prompt_option_values=[True, False],
            default_input="y",
            default_value=True,
        )
        self.buy_mystic_medals = self.get_user_input(
            prompt="Do you want to buy Mystic Medals? (y/n) [y]:  ",
            prompt_options=["y", "n"],
            prompt_option_values=[True, False],
            default_input="y",
            default_value=True,
        )
        self.amount_skystones_to_spent = self.get_user_input(
            prompt="How many Skystones you want to spend? [Empty if you want to use all of your Skystones)]:  ",
            default_input="",
            default_value="-1",
        )
        self.amount_coins_to_spent = self.get_user_input(
            prompt="How many Coins you want to spend? [Empty if you want to use all of your Coins]:  ",
            default_input="",
            default_value="-1",
        )

    def main(self):
        print("Welcome to the Epic 7 Secret Shop Refresher Bot!")
        self.get_initial_user_configuration_info()
        self.should_continue = self.connect_to_android()
        if self.should_continue:
            self.load_image_resources()
            self.check_if_inside_secret_shop()
            time.sleep(3.0)
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
