from holobot import Bot, BotInterface
from holobot.framework.ioc import ServiceCollection, ServiceDiscovery
from holobot.framework.lifecycle import LifecycleManagerInterface
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.database import DatabaseManagerInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.logging.enums import LogLevel

import asyncio
import discord

DEFAULT_BOT_PREFIX = "h!"
DEBUG_MODE_BOT_PREFIX = "h#"

intents = discord.Intents(
	guilds=True,
	members=True,
	emojis=True,
	voice_states=True,
	guild_messages=True,
	guild_reactions=True
)

if __name__ == "__main__":
	event_loop = asyncio.get_event_loop()
	service_collection = ServiceCollection()
	# The idea here is to register the services for each extension independently,
	# however, today it doesn't make sense as they're still in the same package.
	# Therefore, for now we just register everything from the entire package.
	ServiceDiscovery.register_services_by_module("holobot", service_collection)
	# self.register_services_by_module("holobot.extensions.crypto", service_collection)
	
	log = service_collection.get(LogInterface)
	configurator = service_collection.get(ConfiguratorInterface)
	log.log_level = LogLevel.parse(configurator.get("General", "LogLevel", "Information"))
	log.info("[Main] Starting application...")

	bot = Bot(
		service_collection,
		# TODO Guild-specific custom prefix.
		command_prefix = DEFAULT_BOT_PREFIX if not configurator.get("General", "IsDebug", False) else DEBUG_MODE_BOT_PREFIX,
		case_insensitive = True,
		intents = intents,
		loop = event_loop
	)

	service_collection.add_service(bot, BotInterface)

	event_loop.run_until_complete(service_collection.get(DatabaseManagerInterface).upgrade_all())

	lifecycle_manager = service_collection.get(LifecycleManagerInterface)
	event_loop.run_until_complete(lifecycle_manager.start_all())

	if not (discord_token := configurator.get("General", "DiscordToken", "")):
		raise ValueError("The Discord token is not configured.")

	# TODO Automatic extension discovery.
	log.info("[Main] Loading cogs...")
	bot.load_extension("holobot.cogs.general")
	bot.load_extension("holobot.cogs.google")
	bot.load_extension("holobot.extensions.crypto.cogs.crypto")
	bot.load_extension("holobot.extensions.dev.cogs.main")
	bot.load_extension("holobot.extensions.hentai.cogs.main")
	bot.load_extension("holobot.extensions.reminders.cogs.reminders")
	bot.load_extension("holobot.extensions.todo_lists.cogs.main")
	log.info("[Main] Successfully loaded cogs.")

	try:
		log.info("[Main] Application started.")
		event_loop.run_until_complete(bot.start(discord_token))
	except KeyboardInterrupt:
		log.info("[Main] Shutting down due to keyboard interrupt...")
		event_loop.run_until_complete(bot.logout())
	finally:
		event_loop.run_until_complete(lifecycle_manager.stop_all())
		event_loop.run_until_complete(service_collection.close())
		event_loop.close()
	log.info("[Main] Successful shutdown.")
