import datetime
import os
import shutil
import sys
import time

import cv2
import easyocr
import psutil
import uiautomator2 as u2
from colorama import Fore, Style, init
from PIL import Image


class EpicSevenBot:
    def __init__(self):
        # Bluestacks 5 Path
        self.BLUESTACKS_CONF_ADB_PORT_FIELD = "bst.instance.Pie64.status.adb_port"

        # Initialize Colorama
        init()

        # All the variables for images paths
        self.readable_image_path_name = {}
        self.bookmark_image_path = ""
        self.bookmark_buy_confirmation = ""
        self.mystic_medal_image_path = ""
        self.mystic_medal_buy_confirmation = ""
        self.refresh_store_button = ""
        self.refresh_store_confirmation = ""
        self.in_secret_shop = ""
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # All configuration values for the bot to work
        self.should_continue = True
        self.android_instance = None
        self.ocr_instance = easyocr.Reader(["en"], gpu=False)
        self.android_port = None
        self.android_port_txt_path = "android_ADB_port.txt"
        self.buy_bookmarks = True
        self.buy_mystic_medals = True
        self.max_amount_skystones_to_spend = None
        self.max_amount_coins_to_spend = None
        self.save_report = True
        self.current_coins = None
        self.current_skystones = None
        self.BOOKMARK_PRICE = 184_000
        self.AMOUNT_BOOKMARK_PER_BUY = 5
        self.MYSTIC_MEDAL_PRICE = 280_000
        self.AMOUNT_MYSTIC_MEDAL_PER_BUY = 50
        self.SKYSTONES_PER_REFRESH = 3

        # All the report variables
        self.variables_to_show_progress = []
        self.bookmarks_bought = 0
        self.mystic_medals_bought = 0
        self.refreshes_performed = 0
        self.skystones_spent = 0
        self.coins_spent = 0
        self.initial_amount_skystones = 0
        self.initial_amount_coins = 0

    def move_cursor_to_last_line(self):
        # Get the size of the terminal window
        rows, _ = shutil.get_terminal_size()
        # Move the cursor to the last line
        sys.stdout.write(f"\033[{rows};0H")

    def overwrite_last_lines(self, lines_to_overwrite):
        sys.stdout.write("\033[F" * lines_to_overwrite)  # Move cursor up

    def update_print(self, message):
        print("\033[K" + message, end="\r")

    def write_to_file_and_console(self, content, filename):
        # Write content to console
        print(content)
        if self.save_report:
            # Write content to file
            with open(filename, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    def format_number(self, number):
        num_str = str(number)
        result = ""
        for i in range(len(num_str) - 1, -1, -1):
            result = num_str[i] + result
            if (len(num_str) - i) % 3 == 0 and i != 0:
                result = "," + result
        return result

    def show_shopping_report(self):
        """
        This method prints all the shopping statistics.
        """
        self.update_current_skytones_and_coins()
        final_amount_bookmarks = self.bookmarks_bought // self.AMOUNT_BOOKMARK_PER_BUY
        final_amount_mystic_medals = (
            self.mystic_medals_bought // self.AMOUNT_MYSTIC_MEDAL_PER_BUY
        )

        # Create filename with timestamp
        folder_path = "reports"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        filename = f"{folder_path}/shopping_report_{timestamp}.txt"

        self.write_to_file_and_console(
            "-----------------------------------------------------------", filename
        )
        self.write_to_file_and_console(
            f"Should Buy Bookmarks: {'✅' if self.buy_bookmarks else '❌'}", filename
        )
        self.write_to_file_and_console(
            f"Should Buy Mystic Medals: {'✅' if self.buy_mystic_medals else '❌'}",
            filename,
        )
        self.write_to_file_and_console(
            f"Max amount of Skystones to spend: {self.format_number(self.max_amount_skystones_to_spend) if self.max_amount_skystones_to_spend > 0 else '♾️'}",
            filename,
        )
        self.write_to_file_and_console(
            f"Max amount of Coins to spend: {self.format_number(self.max_amount_coins_to_spend) if self.max_amount_coins_to_spend > 0 else '♾️'}",
            filename,
        )
        self.write_to_file_and_console(
            f"Bookmarks Bought: {final_amount_bookmarks} ({self.format_number(self.bookmarks_bought)} Bookmarks)",
            filename,
        )
        self.write_to_file_and_console(
            f"Mystic Medals Bought: {final_amount_mystic_medals} ({self.format_number(self.mystic_medals_bought)} Mystic Medals)",
            filename,
        )
        self.write_to_file_and_console(
            f"Refreshes Perfomed: {self.format_number(self.refreshes_performed)}",
            filename,
        )
        self.write_to_file_and_console(
            f"Initial Skystones: {self.format_number(self.initial_amount_skystones)}",
            filename,
        )
        self.write_to_file_and_console(
            f"Skystones Spent: {self.format_number(self.skystones_spent)}",
            filename,
        )
        self.write_to_file_and_console(
            f"Initial Coins: {self.format_number(self.initial_amount_coins)}", filename
        )
        self.write_to_file_and_console(
            f"Coins Spent: {self.format_number(self.coins_spent)}", filename
        )
        if self.refreshes_performed > 0:
            bookmark_ratio = final_amount_bookmarks / self.refreshes_performed
            bookmark_frequency = 1 / bookmark_ratio if bookmark_ratio > 0 else 0
            mystic_medals_ratio = final_amount_mystic_medals / self.refreshes_performed
            mystic_medals_frequency = (
                1 / mystic_medals_ratio if mystic_medals_ratio > 0 else 0
            )

            if bookmark_frequency > 0:
                self.write_to_file_and_console(
                    f"You encountered 5 Bookmarks every { int(bookmark_frequency) } refreshes",
                    filename,
                )

            if mystic_medals_frequency > 0:
                self.write_to_file_and_console(
                    f"You encountered 50 Mystic Medals every { int(mystic_medals_frequency) } refreshes",
                    filename,
                )

        self.write_to_file_and_console(
            "-----------------------------------------------------------", filename
        )

    def display_progress_bar(self, max_value, current_value, increment_by=1):
        percentage = (
            int((current_value / max_value) * 100)
            if max_value > current_value + increment_by
            else 100
        )
        bar = f"[{'=' * percentage}{'>' if percentage < 100 else '='}{' ' * (100 - percentage)}] {percentage}%\n"
        if percentage < 20:
            return Fore.LIGHTRED_EX + bar + Fore.WHITE
        elif percentage < 40:
            return Fore.LIGHTMAGENTA_EX + bar + Fore.WHITE
        elif percentage < 60:
            return Fore.LIGHTBLUE_EX + bar + Fore.WHITE
        elif percentage < 80:
            return Fore.LIGHTCYAN_EX + bar + Fore.WHITE
        elif percentage >= 80 and percentage < 100:
            return Fore.LIGHTYELLOW_EX + bar + Fore.WHITE
        elif percentage == 100:
            return Fore.LIGHTGREEN_EX + bar + Fore.WHITE

    def display_secret_shop_progress(self, first_display=False):
        if not first_display:
            progress_bar_line = 0
            if self.max_amount_skystones_to_spend != -1:
                progress_bar_line += 1
            if self.max_amount_coins_to_spend != -1:
                progress_bar_line += 1
            self.overwrite_last_lines(
                len(self.variables_to_show_progress) + progress_bar_line
            )

        progress = ""
        if self.max_amount_skystones_to_spend != -1:
            progress += f"Amount of Skystones spent: {self.format_number(self.skystones_spent)} out of {self.format_number(self.max_amount_skystones_to_spend)}\n"
            progress += f"{self.display_progress_bar(max_value=self.max_amount_skystones_to_spend, current_value=self.skystones_spent)}"
        if self.max_amount_coins_to_spend != -1:
            progress += f"Amount of Coins spent: {self.format_number(self.coins_spent)} out of {self.format_number(self.max_amount_coins_to_spend)}\n"
            progress += f"{self.display_progress_bar(max_value=self.max_amount_coins_to_spend, current_value=self.coins_spent)}"
        if self.buy_bookmarks:
            final_amount_bookmarks = (
                self.bookmarks_bought // self.AMOUNT_BOOKMARK_PER_BUY
            )
            progress += f"Bookmarks Bought: {final_amount_bookmarks} ({self.format_number(self.bookmarks_bought)} Bookmarks)\n"
        if self.buy_mystic_medals:
            final_amount_mystic_medals = (
                self.mystic_medals_bought // self.AMOUNT_MYSTIC_MEDAL_PER_BUY
            )
            progress += f"Mystic Medals Bought: {final_amount_mystic_medals} ({self.format_number(self.mystic_medals_bought)} Mystic Medals)\n"
        print(progress, end="")
        self.move_cursor_to_last_line()

    def load_image_resources(self):
        """
        This method loads all the images required for the script
        to match on the android instance during runtime.
        """
        try:
            self.update_print(
                Fore.YELLOW + "Loading the image resources ..." + Fore.WHITE
            )

            self.bookmark_image_path = os.path.join(
                self.current_dir, "image_resources", "bookmark_shop_entry.png"
            )

            self.bookmark_buy_confirmation = os.path.join(
                self.current_dir, "image_resources", "bookmark_buy_confirmation.png"
            )

            self.mystic_medal_image_path = os.path.join(
                self.current_dir, "image_resources", "mystic_medal_shop_entry.png"
            )

            self.mystic_medal_buy_confirmation = os.path.join(
                self.current_dir, "image_resources", "mystic_medal_buy_confirmation.png"
            )

            self.refresh_store_button = os.path.join(
                self.current_dir, "image_resources", "refresh_button.png"
            )

            self.refresh_store_confirmation = os.path.join(
                self.current_dir, "image_resources", "refresh_store_confirmation.png"
            )

            self.in_secret_shop = os.path.join(
                self.current_dir, "image_resources", "secret_shop.png"
            )

            self.readable_image_path_name = {
                self.bookmark_image_path: "Bookmark",
                self.bookmark_buy_confirmation: "Bookmark Buy Confirmation",
                self.mystic_medal_image_path: "Mystic Medal",
                self.mystic_medal_buy_confirmation: "Mystic Medal Buy Confirmation",
                self.refresh_store_button: "Refresh Button",
                self.refresh_store_confirmation: "Refresh Store Confirmation",
                self.in_secret_shop: "Secrect Shop",
            }

            print(Fore.GREEN + "Image resources loaded successfully!" + Fore.WHITE)
        except Exception as e:
            print(
                Fore.RED + f"There was an error loading the resources: {e}" + Fore.WHITE
            )
            self.should_continue = False

    def connect_to_android(self):
        """
        This method handles the connection of the script to android instance.
        """
        try:
            # Connect to BlueStacks Emulator that has ADB enabled
            self.update_print("Connecting to Bluestack instance ...")
            self.android_instance = u2.connect(f"127.0.0.1:{self.android_port}")
            bluestack_5 = self.android_instance.info

            if bluestack_5["currentPackageName"] != "com.stove.epic7.google":
                raise Exception(
                    "Epic Seven is not opened, please try again after opening the app."
                )
            print(Fore.GREEN + "Connected to BlueStacks successfully!")
            return True

        except Exception as e:
            if "Invalid version: ''" in e.args:
                _ = input(
                    "Please go to your ATX App and click the 启动UIAUTOMATOR button. Press any Key when done: "
                )
                return self.connect_to_android()
            else:
                print(Fore.RED + f"Failed to connect to BlueStacks: {e}" + Fore.WHITE)
                return False

    def extract_numbers_from_image(self, resource_image):
        """
        This method reads the screen next to an image and returns the text read.
        """
        numbers = self.ocr_instance.readtext(resource_image)
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
                # Get height and width of the matched image
                h, w = image_to_search.shape[:-1]
                # Calculate lower right corner coordinates, to be able to click the buy button
                x2, y2 = x + w - 20, y + h - 20
                return True, x2, y2
            else:
                # print(f"{self.readable_image_path_name.get(search_image_path, 'Resource')} not found on screen.")
                return False, 0, 0
        except Exception as e:
            print(Fore.RED + f"There was an error: {e}" + Fore.WHITE)
            return False, 0, 0

    def buy_resource(self, x, y, resource="bookmark"):
        """
        This method handles the logic for buying bookmarks and mystic medals.
        """
        # We open the resource buying confirmation menu
        self.android_instance.double_click(x, y)

        buy_confirmation = (
            self.bookmark_buy_confirmation
            if resource == "bookmark"
            else self.mystic_medal_buy_confirmation
        )
        time.sleep(0.5)
        match_found, x, y = self.match_android_screen_to_image(buy_confirmation)

        if match_found:
            time.sleep(0.5)
            self.android_instance.double_click(x, y)
            return True
        else:
            # print("I am unable to see the buy confirmation!")
            return False

    def update_current_skytones_and_coins(self, initial_setup=False):
        """
        This method checks if spending limit has been reached for Skystones or Coins.
        """
        screenshot_path = os.path.join(
            self.current_dir, "image_resources", "resources_screenshot.png"
        )
        screenshot = self.android_instance.screenshot(format="opencv")
        screenshot_image = Image.fromarray(screenshot)
        # Here is region in which the account's Coins and Skystones are located
        region = (
            980,  # Initial X
            0,  # Initial Y
            1300,  # Final X
            62,  # Final Y
        )
        # Can check this with cropped_image.show()
        cropped_image = screenshot_image.crop(region)
        cropped_image.save(screenshot_path)
        numbers = self.extract_numbers_from_image(screenshot_path)
        try:
            self.current_coins = int(numbers[0][1].replace(",", "").replace(" ", ""))
            self.current_skystones = int(
                numbers[1][1].replace(",", "").replace(" ", "")
            )
        except ValueError:
            time.sleep(5)
            self.extract_numbers_from_image(screenshot_path)
        if initial_setup:
            self.initial_amount_coins = self.current_coins
            self.initial_amount_skystones = self.current_skystones

    def get_resources(self):
        """
        This method handles the logic for searching/buying bookmarks and mystic medals.
        """
        if self.buy_bookmarks:
            # Search for Bookmarks
            result, x, y = self.match_android_screen_to_image(self.bookmark_image_path)
            if result:
                self.update_current_skytones_and_coins()
                if (
                    self.max_amount_coins_to_spend == -1
                    or self.max_amount_coins_to_spend
                    >= self.coins_spent + self.BOOKMARK_PRICE
                ):
                    if self.current_coins >= self.BOOKMARK_PRICE:
                        if self.buy_resource(x, y):
                            self.bookmarks_bought += self.AMOUNT_BOOKMARK_PER_BUY
                            self.coins_spent += self.BOOKMARK_PRICE
                            self.display_secret_shop_progress()
                    else:
                        self.should_continue = False
                        print(
                            Fore.MAGENTA + "You don't have any Coins left!" + Fore.WHITE
                        )
                else:
                    self.should_continue = False
                    print(
                        Fore.MAGENTA
                        + "Max amount of {self.coins_spent} Coins to spend reached!"
                        + Fore.WHITE
                    )
        if self.buy_mystic_medals:
            # Search for Mystic Medals
            result, x, y = self.match_android_screen_to_image(
                self.mystic_medal_image_path
            )
            if result:
                self.update_current_skytones_and_coins()
                # If there is no limit to spend coins (-1) or we haven't reached the max amount of
                if (
                    self.max_amount_coins_to_spend == -1
                    or self.max_amount_coins_to_spend
                    >= self.coins_spent + self.MYSTIC_MEDAL_PRICE
                ):
                    if self.current_coins >= self.MYSTIC_MEDAL_PRICE:
                        if self.buy_resource(x, y, "mystic_medal"):
                            self.mystic_medals_bought += (
                                self.AMOUNT_MYSTIC_MEDAL_PER_BUY
                            )
                            self.coins_spent += self.MYSTIC_MEDAL_PRICE
                            self.display_secret_shop_progress()
                    else:
                        self.should_continue = False
                        print(
                            Fore.MAGENTA + "You don't have any Coins left!" + Fore.WHITE
                        )
                else:
                    self.should_continue = False
                    print(
                        Fore.MAGENTA
                        + f"Max amount of {self.coins_spent} Coins to spend reached!"
                        + Fore.WHITE
                    )

    def refresh_store(self):
        """
        This method handles the logic for refreshing the store.
        """
        self.update_current_skytones_and_coins()
        if (
            self.max_amount_skystones_to_spend == -1
            or self.max_amount_skystones_to_spend
            >= self.skystones_spent + self.SKYSTONES_PER_REFRESH
        ):
            if self.current_skystones >= self.SKYSTONES_PER_REFRESH:
                match_found, x, y = self.match_android_screen_to_image(
                    self.refresh_store_button
                )
                if not match_found:
                    # print("I am unable to see the refresh button!")
                    pass
                else:
                    self.android_instance.double_click(x, y)
                    time.sleep(0.3)
                    match_found, x, y = self.match_android_screen_to_image(
                        self.refresh_store_confirmation
                    )
                    if not match_found:
                        # print("I am unable to see the refresh confirmation pop up!")
                        pass
                    else:
                        self.android_instance.double_click(x, y)
                        self.skystones_spent += self.SKYSTONES_PER_REFRESH
                        self.refreshes_performed += 1
                        self.display_secret_shop_progress()
            else:
                self.should_continue = False
                print(Fore.MAGENTA + "You don't have any Skystones left!" + Fore.WHITE)
        else:
            self.should_continue = False
            print(
                Fore.MAGENTA
                + f"Max amount of {self.skystones_spent} Skystones to spend reached!"
                + Fore.WHITE
            )

    def check_if_inside_secret_shop(self):
        """
        This method stops execution of the script if the E7 game is not inside Garo's Secret Shop.
        """
        match_found, _, _ = self.match_android_screen_to_image(self.in_secret_shop)
        if not match_found:
            print(
                Fore.RED
                + "This bot only works inside Garo's Tabern Secret Shop!"
                + Fore.WHITE
            )
            _ = input(
                "Please move to Garo's Tabern Secret Shop and press"
                + Fore.GREEN
                + " Enter "
                + Fore.WHITE
                + "when done: "
            )
            self.check_if_inside_secret_shop()
        else:
            print("Hi Garo, I'll be ordering the usual!\n")

    def secret_shop_bot(self):
        """
        This method contains the logic for matching, clicking, buying and refreshing the shop.
        """
        self.display_secret_shop_progress(first_display=True)
        while self.should_continue:
            time.sleep(1)
            # To get rid of Heroe Dispatches Returning
            self.android_instance.double_click(1120, 730)
            self.get_resources()
            self.android_instance.swipe(1150, 720, 1130, 430, 0.1)
            # To get rid of Heroe Dispatches Returning
            self.android_instance.double_click(1120, 730)
            self.get_resources()
            self.refresh_store()
        print(
            Fore.WHITE + "The Epic 7 Secret Shop Refresher Bot run has finished. Bye!"
        )

    def get_user_input(
        self,
        prompt,
        prompt_options=None,
        prompt_option_values=None,
        default_input=None,
        default_value=None,
        require_positive_integer=False,
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

            if require_positive_integer:
                # Check if the input is a positive integer
                try:
                    user_input_int = int(user_input)
                    if user_input_int > 0:
                        return user_input_int
                except ValueError:
                    pass

            if prompt_options:
                # User inputted one of the prompt_options
                if user_input in prompt_options:
                    incorrect_input = False
                    if prompt_option_values:
                        return prompt_option_values[prompt_options.index(user_input)]
                    else:
                        return user_input
            elif not require_positive_integer:
                incorrect_input = False
                return user_input

    def get_all_system_drives(self):
        """
        This method gets all drives names of the system
        """
        drive_info = []
        partitions = psutil.disk_partitions(all=True)
        for partition in partitions:
            drive_info.append(partition.device)
        return drive_info

    def find_bluestacks_conf(self, available_system_drives):
        self.update_print(Fore.WHITE + "Finding Bluestack Configuration ...")
        probable_paths = [
            "{}Program Files\\BlueStacks_nxt",
            "{}Program Files (x86)\\BlueStacks_nxt",
            "{}ProgramData\\BlueStacks_nxt",
            "{}bluestacks\\BlueStacks_nxt",
        ]

        for drive in available_system_drives:
            for path_template in probable_paths:
                path = path_template.format(drive)
                self.update_print(f"Searching on {path}...")
                if os.path.exists(path):
                    conf_path = os.path.join(path, "bluestacks.conf")
                    if os.path.exists(conf_path):
                        return conf_path

        if (
            self.get_user_input(
                prompt="It seems your local installation of Bluestacks is not on a common place, do you want to search your whole system for it? This may take a while ("
                + Fore.GREEN
                + "y"
                + Fore.WHITE
                + "/"
                + Fore.RED
                + "n"
                + Fore.WHITE
                + ") ["
                + Fore.RED
                + "n"
                + Fore.WHITE
                + "]:  ",
                prompt_options=["y", "n"],
                prompt_option_values=[True, False],
                default_input="n",
                default_value=False,
            )
            is True
        ):
            for drive in available_system_drives:
                for root, drive, files in os.walk(drive):
                    if "bluestacks.conf" in files:
                        return os.path.join(root, "bluestacks.conf")
        return None

    def get_adb_port(self):
        """
        This method searches the bluestacks.conf for the current port in which ADB is running
        """
        drive_names = self.get_all_system_drives()
        bluestacks_conf_path = self.find_bluestacks_conf(drive_names)
        if bluestacks_conf_path:
            print(
                Fore.GREEN
                + f"Found Bluestacks configuration file at {bluestacks_conf_path}"
                + Fore.WHITE
            )
            with open(bluestacks_conf_path, "r") as file:
                for line in file:
                    if self.BLUESTACKS_CONF_ADB_PORT_FIELD in line:
                        self.android_port = int(line.split("=")[1].replace('"', ""))
                        print(f"Your ADB port is: {self.android_port}")
                        break
        else:
            print(Fore.RED + "Bluestacks configuration file not found." + Fore.WHITE)

    def check_stored_android_port(self):
        """
        This method allows to handle preserving the ADB_port variable throughout different script runs.
        """
        self.get_adb_port()
        if not self.android_port:
            port_found = False
            if os.path.exists(self.android_port_txt_path):
                with open(self.android_port_txt_path, "r") as file:
                    first_line = file.readline().strip()
                    if first_line.startswith("ADB_port="):
                        self.android_port = first_line.split("=")[1]
                        port_found = True
                        print(
                            Fore.GREEN
                            + f"Stored ADB Port found: {self.android_port}"
                            + Fore.WHITE
                        )
            if not os.path.exists(self.android_port_txt_path) or not port_found:
                with open(self.android_port_txt_path, "w") as file:
                    should_store_ADB_port = self.get_user_input(
                        prompt="I see you do not have your ADB port stored yet. You want to store it? ("
                        + Fore.GREEN
                        + "y"
                        + Fore.WHITE
                        + "/"
                        + Fore.RED
                        + "n"
                        + Fore.WHITE
                        + ") ["
                        + Fore.GREEN
                        + "y"
                        + Fore.WHITE
                        + "]: ",
                        prompt_options=["y", "n"],
                        prompt_option_values=[True, False],
                        default_input="y",
                        default_value=True,
                    )
                    self.android_port = self.get_user_input(
                        prompt="In which port is your Android instance ADB running?:  ",
                        allow_positive_integer=True,
                    )
                    if should_store_ADB_port:
                        file.write(f"ADB_port={self.android_port}\n")
                        print(Fore.GREEN + "ADB Port Stored!" + Fore.WHITE)

    def get_initial_user_configuration_info(self):
        """
        This method allows the user to go through the configuration menu for the
        script runtime decisions returning its position on the android screen.
        """
        self.check_stored_android_port()
        self.buy_bookmarks = self.get_user_input(
            prompt="Do you want to buy Bookmarks? ("
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "/"
            + Fore.RED
            + "n"
            + Fore.WHITE
            + ") ["
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "]:  ",
            prompt_options=["y", "n"],
            prompt_option_values=[True, False],
            default_input="y",
            default_value=True,
        )
        if self.buy_bookmarks:
            self.variables_to_show_progress.append(self.buy_bookmarks)
        self.buy_mystic_medals = self.get_user_input(
            prompt="Do you want to buy Mystic Medals? ("
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "/"
            + Fore.RED
            + "n"
            + Fore.WHITE
            + ") ["
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "]:  ",
            prompt_options=["y", "n"],
            prompt_option_values=[True, False],
            default_input="y",
            default_value=True,
        )
        if self.buy_mystic_medals:
            self.variables_to_show_progress.append(self.buy_mystic_medals)
        self.max_amount_skystones_to_spend = self.get_user_input(
            prompt="How many Skystones you want to spend? [Empty if you want to use all of your Skystones]:  ",
            default_input="",
            default_value=-1,
            require_positive_integer=True,
        )
        if self.max_amount_skystones_to_spend >= 0:
            self.variables_to_show_progress.append(self.max_amount_skystones_to_spend)
        self.max_amount_coins_to_spend = self.get_user_input(
            prompt="How many Coins you want to spend? [Empty if you want to use all of your Coins]:  ",
            default_input="",
            default_value=-1,
            require_positive_integer=True,
        )
        if self.max_amount_coins_to_spend >= 0:
            self.variables_to_show_progress.append(self.max_amount_coins_to_spend)
        self.save_report = self.get_user_input(
            prompt="Do you want to save the shop report upon exit? ("
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "/"
            + Fore.RED
            + "n"
            + Fore.WHITE
            + ") ["
            + Fore.GREEN
            + "y"
            + Fore.WHITE
            + "]:  ",
            prompt_options=["y", "n"],
            prompt_option_values=[True, False],
            default_input="y",
            default_value=True,
        )

    def main(self):
        print(Style.BRIGHT)
        print(Fore.CYAN + "Welcome to the Epic 7 Secret Shop Refresher Bot!\n")
        print(
            Fore.RED
            + "NOTE: "
            + Fore.YELLOW
            + "At any time you can press"
            + Fore.GREEN
            + " Ctrl+C"
            + Fore.YELLOW
            + " to stop the Bot execution"
        )
        print(
            Fore.RED
            + "NOTE: "
            + Fore.YELLOW
            + "Please cancel any pending Dispatch Mission in your High Command to avoid weird behaviors"
        )
        self.get_initial_user_configuration_info()
        self.should_continue = self.connect_to_android()
        if self.should_continue:
            try:
                self.load_image_resources()
                self.check_if_inside_secret_shop()
                self.update_current_skytones_and_coins(initial_setup=True)
                self.secret_shop_bot()
            except KeyboardInterrupt:
                print(
                    Fore.GREEN
                    + "Ctrl+C"
                    + Fore.WHITE
                    + " pressed. Exiting gracefully..."
                )
            finally:
                self.show_shopping_report()
                print(Style.RESET_ALL)


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
    # for i in range(100):
    #     print(bot.display_progress_bar(max_value=100, current_value=i))
