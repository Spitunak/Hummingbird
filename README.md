Hummingbird is a Discord bot that manages a centralized ban list using a simple .txt file. The file contains user IDs that are automatically processed by the bot.

How it works:

The bot reads the configured .txt file every 2 minutes.

All Discord user IDs listed in the file are checked.

If a listed user is found on the server, they are automatically banned.

The scanning process runs continuously in the background.
