# Welcome

Holo is a gradually growing bot with Discord integration. As it is a hobby project, there is no specific goal: whatever sounds like a good idea and has some use gets added over time.

# Features

Below are some of the feature groups currently available:

* General functionality (avatar, emoji, dice)
* Development related functionality (module management, ping, logging)
* Google text and image search
* Reminders
* To-do lists
* Cryptocurrency information

For details about each group, please refer to the source code or the bot's help menu.

# Technologies

Below are some of the technologies used by this project:
* [Python 3](https://www.python.org/)
* [discord.py](https://github.com/Rapptz/discord.py)
* [asyncpg](https://github.com/MagicStack/asyncpg)
* [pytz](https://pythonhosted.org/pytz)
* [tzlocal](https://github.com/regebro/tzlocal)
* [Binance API](https://developers.binance.com)
  
# Installation

## Inviting the official instance to your server

It is suggested to use the official instance of this bot which you can invite to your Discord server by using the following authorization link:
https://discord.com/api/oauth2/authorize?client_id=791766309611634698&permissions=122707586134&scope=bot%20applications.commands

Currently, the bot requires administrator permissions to work correctly, which will be changed in the future when proper permission handling is implemented. If you deny some of the permissions, some features may not work as expected.

This instance of the bot is automatically deployed from the _main_ branch with new commits.

## Hosting your own instance

**Python 3.8 or higher is required.**

After cloning the repository, you will have to make sure that all the dependencies are installed correctly. This can be achieved by the following command:

```sh
# All of the requirements are specified by a text file.
python3 -m pip install -r requirements.txt
```

As we are talking about a Discord bot here, you will have to create an official application to acquire tokens necessary for authentication with the servers. Please, refer to [Discord's development portal](https://discord.com/developers/docs/intro) for details.

Depending on your environment (such as [Heroku](https://www.heroku.com)), you can use either the *config.json* file or your system's environment variables to specify the configuration. For each available parameter and their default values, refer to the included [config.json](https://github.com/rexor12/holobot/blob/main/config.json) file. Below is a sample:

```json
{
    "General": {
        "parameters": {
            "DiscordToken": "<your Discord token goes here>",
            "LogLevel": "Information"
        }
    }
}
```

# Contribution

Your contribution is more than welcome any time, be it ideas, suggestions, bug reports, bug fixes or new features.

There is no specific process for now, therefore - depending on the type of contribution - I suggest either creating an [issue](https://github.com/rexor12/holobot/issues) or forking the repository and creating a [pull request](https://github.com/rexor12/holobot/pulls).

Thank you!
