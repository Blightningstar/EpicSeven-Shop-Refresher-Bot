This is a python project that automates the boring aspect of refreshing the shop in the mobile gacha game Epic Seven, in order to get as many bookmarks and red medallions required to buy champions in the game.

The program requires the user to run the game in bluestacks.

The bot registers the amount of resources (Gold & Skystones available) present on the screen and while asking via CLI how much resources it should use and if it should buy Bookmarks / Red Medallions or both, it then continues to refresh the shop and stops once any of those resources are depleted or the amount inputed is reached.

The steps will be to:

- Check the first 2 items in the shop to see if they are bookmarks or medallions
    - If any of the first 2 items result positive, we'll check our Resources and if available, we'll buy them
- Scroll the shop to see the remaining 4 items
    - If any of the remaining 4 items result positive, we'll check our Resources and if available, we'll buy them
- We'll hit the Refresh Shop Button if skystones are available, then we'll hit confirm in the confirmation modal
- The process continues until either we ran out of Gold or Skystones or the presets chosen by the user via the CLI at the beginning of the program dictate so
- The program will then display how many resources did it use, how many Bookmarks and Red Medallions found and what percentages encountered while refreshing the shop.

