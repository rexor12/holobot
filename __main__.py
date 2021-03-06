from holobot.bot import Bot
from holobot.bot_interface import BotInterface
from holobot.configs.configurator_interface import ConfiguratorInterface
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.dependency_injection.service_collection import ServiceCollection
from holobot.dependency_injection.service_discovery import ServiceDiscovery
from holobot.lifecycle.lifecycle_manager_interface import LifecycleManagerInterface
from holobot.logging.log_interface import LogInterface
from holobot.logging.log_level import LogLevel

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
	ServiceDiscovery().register_services(service_collection)
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
	bot.load_extension("holobot.cogs.development")
	bot.load_extension("holobot.cogs.general")
	bot.load_extension("holobot.cogs.google")
	bot.load_extension("holobot.crypto.cogs.crypto")
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
