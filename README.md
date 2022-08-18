# Welcome

Holo is a gradually growing bot with Discord integration. As it is a hobby project, there is no specific goal: whatever sounds like a good idea and has some use gets added over time.

# Features

Below are some of the feature groups currently available:

* General (avatar, emoji, dice, 8-ball)
* Administration (command usage permissions)
* Moderation (manual/auto mute, kick, ban, logging)
* Google text and image search
* Reminders
* To-do lists
* Weather information
* Cryptocurrency information (provided by Binance)

For details about each group, please refer to the source code or the bot's help menu.

# Technologies

Below are some of the technologies used by this project:
* [Python 3](https://www.python.org/)
* [hikari](https://github.com/hikari-py)
* [kanata](https://github.com/rexor12/kanata)
* [asyncpg](https://github.com/MagicStack/asyncpg)
* [tzlocal](https://github.com/regebro/tzlocal)
* [Binance API](https://developers.binance.com)
* [Google API](https://developers.google.com/custom-search/v1/overview)

# Installation

## Inviting the official instance to your server

While you are free to host your own instance of the bot, I would be grateful if you used the official instance that I maintain so that Holo can grow by getting more valuable feedback.

You can use the following authorization link to invite the official instance:
https://discord.com/api/oauth2/authorize?client_id=791766309611634698&permissions=122707586134&scope=bot%20applications.commands

To enable additional features of the bot, you can provide the necessary permissions in Discord for the bot's role or the bot user itself. When a required permission is missing, the bot should be able to tell you upon invoking the command.

This instance of the bot is deployed from the _main_ branch, therefore it is usually the latest and greatest version.

## Hosting your own instance

**Python 3.10 or higher is required.**

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

Your contribution is welcome any time, be it suggestions, bug reports, bug fixes or new features.

There is no specific process for now, therefore - depending on the type of contribution - I suggest either creating an [issue](https://github.com/rexor12/holobot/issues) or forking the repository and creating a [pull request](https://github.com/rexor12/holobot/pulls).

Thank you!
