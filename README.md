# Welcome

Holo is a gradually growing bot with Discord integration. As it is a hobby project, there is no specific goal: when I have an idea I think is good, I implement it. Sometimes these may be new business features and technical refactors at other times.

# Features

Below are some of the feature groups currently available:

* General (avatar, banner, emoji, dice, 8-ball)
* Moderation (manual/auto mute, kick, ban, logging)
* Giveaways (Epic Games Store)
* Reminders
* To-do lists
* Weather information (OpenWeather)
* Google (text, image)
* Anime reactions (Waifu.pics)
* Administration (command usage permissions)

For details about each group, please refer to the source code or the bot's commands on Discord.

# Installation

## Inviting the official instance to your server

While you are free to host your own instance of the bot, I would be grateful if you used the official instance that I maintain so that Holo can grow by getting more valuable feedback.

You can use the following authorization link to invite the official instance:
https://discord.com/api/oauth2/authorize?client_id=791766309611634698&permissions=122707586134&scope=bot

To enable additional features of the bot, you can provide the necessary permissions in Discord for the bot's role or the bot user itself. When a required permission is missing, the bot should be able to tell you upon invoking the command.

This instance of the bot is deployed from the latest stable branch (develop/x.x.x) while the new development happens on the _main_ branch in an isolated environment.

## Hosting your own instance

**Python 3.10 or higher is required.**

### Docker

If you have Docker installed, clone the repository and build the image first:
```sh
docker build -t rexor12/holobot .
```

Open the `.env` file in the secrets directory and configure the necessary environment variables:
```ini
HOLO_ENVIRONMENT=docker
HOLO_BOT_TOKEN=<your Discord bot token here>
HOLO_DEVELOPMENT_SERVER_ID=<your own Discord server ID here>
...other settings...
```

Once that's done, fire up the container:
```sh
docker-compose up -d
```

### Standalone

If Docker is not an option for you, you may choose to host the bot directly.

After cloning the repository, you will have to make sure that all the dependencies are installed correctly. This can be achieved by the following command:

```sh
# All of the requirements are specified by a text file.
python -m pip install -r requirements.txt
```

As we are talking about a Discord bot here, you will have to create an official application to acquire tokens necessary for authentication with the servers. Please, refer to [Discord's development portal](https://discord.com/developers/docs/intro) for details.

Depending on your environment (such as [Heroku](https://www.heroku.com)), you can use either the *config.json* file or your system's environment variables to specify the configuration. For each available parameter and their default values, refer to the included [config.json](https://github.com/rexor12/holobot/blob/main/config.json) file. Below is a sample:

```json
{
    "Core": {
        "DiscordOptions": {
            "DiscordToken": "<your Discord token goes here>"
        }
    }
}
```

# Technologies

Below are some of the technologies used by this project:
* [Python 3](https://www.python.org/)
* [hikari](https://github.com/hikari-py)
* [Google API](https://developers.google.com/custom-search/v1/overview)
* [OpenWeather API](https://openweathermap.org/api)
* [Waifu.pics API](https://waifu.pics/docs)

Please, refer to the requirements.txt file for a list of PyPI packages.

# Contribution

Any form of contribution is appreciated, therefore if you would like to do so, you can either create an [issue](https://github.com/rexor12/holobot/issues) or fork the repository and create a [pull request](https://github.com/rexor12/holobot/pulls).
