import asyncio
import logging
import sys
from typing import Any

import structlog
from kanata import LifetimeScope
from kanata.catalogs import InjectableCatalogBuilder
from kanata.graphs.exceptions import CyclicGraphException
from kanata.models import InjectableScopeType

from holobot.framework import Kernel
from holobot.framework.caching import ObjectCache
from holobot.framework.configs import Configurator, OptionsProvider
from holobot.framework.logging import DefaultLoggerFactory, LoggerManager, LoggerWrapper
from holobot.framework.logging.handlers import ForwardEntryHandler
from holobot.framework.logging.processors import ignore_loggers_by_name
from holobot.framework.system import Environment
from holobot.sdk.caching import ICache, IObjectCache
from holobot.sdk.configs import IConfigurator, IOptions
from holobot.sdk.lifecycle import IStartable
from holobot.sdk.logging import ILoggerFactory, ILoggerManager
from holobot.sdk.logging.enums import LogLevel
from holobot.sdk.system import IEnvironment

if __name__ != "__main__":
    sys.exit(0)

environment = Environment()
configurator = Configurator(environment)
log_level = LogLevel.parse(
    configurator.get_parameter(("Core", "EnvironmentOptions"), "LogLevel", "Information")
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        ignore_loggers_by_name("Kanata"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper("iso"),
        structlog.dev.ConsoleRenderer()
    ],
    # TODO Replace with an AsyncBoundLogger when it's officially supported.
    # https://github.com/hynek/structlog/issues/354
    wrapper_class=LoggerWrapper,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger(logger_name="Holobot")

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        ForwardEntryHandler(logger)
    ]
)

logger_manager = LoggerManager()
logger_manager.set_min_log_level(log_level)

logger_factory = DefaultLoggerFactory(logger_manager)

logger.info("Configured logging", log_level=log_level.name or log_level.value)

# The idea here is to register the services for each extension independently,
# however, today it doesn't make sense as they're still in the same package.
# Therefore, for now we just register everything from the entire package.
catalog_builder = InjectableCatalogBuilder()
catalog_builder.add_module("holobot")
catalog_builder.register_instance(logger_manager, (ILoggerManager,))
catalog_builder.register_instance(logger_factory, (ILoggerFactory,))
catalog_builder.register_instance(environment, (IEnvironment,))
catalog_builder.register_instance(configurator, (IConfigurator,))
catalog_builder.register_generic(OptionsProvider, (IOptions,), InjectableScopeType.SINGLETON)
catalog_builder.register_instance(ObjectCache(logger_factory), (ICache[Any, Any], IObjectCache, IStartable))
logger.info("Loaded all modules")

scope = LifetimeScope(catalog_builder.build())
try:
    logger.info("Starting the kernel...")
    asyncio.run(scope.resolve(Kernel).run())
    logger.info("The kernel has stopped")
except CyclicGraphException as error:
    logger.fatal(
        "Failed to resolve the services, because there is a cycle in the dependency graph",
        nodes=", ".join(map(str, error.nodes))
    )
