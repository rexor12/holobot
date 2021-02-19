from holobot.crypto.alert_manager import AlertManager, AlertManagerInterface
from holobot.crypto.crypto_updater import CryptoUpdater
from holobot.crypto.database.crypto_migration import CryptoMigration
from holobot.crypto.database.alert_migration import AlertMigration
from holobot.crypto.models.symbol_update_event import SymbolUpdateEvent
from holobot.crypto.repositories.crypto_repository import CryptoRepository
from holobot.crypto.repositories.crypto_repository_interface import CryptoRepositoryInterface
from holobot.database.database_manager import DatabaseManager
from holobot.database.database_manager_interface import DatabaseManagerInterface
from holobot.database.migration.migration_interface import MigrationInterface
from holobot.dependency_injection.providers.simple_service_provider import SimpleServiceProvider
from holobot.dependency_injection.service_collection import ServiceCollection
from holobot.display.discord import Discord
from holobot.display.display_interface import DisplayInterface
from holobot.lifecycle.lifecycle_manager import LifecycleManager
from holobot.lifecycle.lifecycle_manager_interface import LifecycleManagerInterface
from holobot.lifecycle.startable_interface import StartableInterface
from holobot.logging.console_log import ConsoleLog
from holobot.logging.log_interface import LogInterface
from holobot.network.http_client_pool import HttpClientPool
from holobot.network.http_client_pool_interface import HttpClientPoolInterface
from holobot.reactive.listener_interface import ListenerInterface
from holobot.security.credential_manager_interface import CredentialManagerInterface
from holobot.security.environment_credential_manager import EnvironmentCredentialManager
from holobot.security.file_credential_manager import FileCredentialManager
from holobot.security.global_credential_manager import GlobalCredentialManager
from holobot.security.global_credential_manager_interface import GlobalCredentialManagerInterface

# TODO Implement automatic service discovery. (Look at all those imports!)
# Maybe a good idea here is to put these in the module __init__.py files?
class ServiceDiscovery:
    def register_services(self, service_collection: ServiceCollection):
        provider = SimpleServiceProvider()
        provider.register(CredentialManagerInterface, EnvironmentCredentialManager)
        provider.register(CredentialManagerInterface, FileCredentialManager)
        provider.register(GlobalCredentialManagerInterface, GlobalCredentialManager)
        provider.register(HttpClientPoolInterface, HttpClientPool)
        provider.register(CryptoRepositoryInterface, CryptoRepository)
        provider.register(StartableInterface, CryptoUpdater)
        provider.register(LifecycleManagerInterface, LifecycleManager)
        provider.register(DatabaseManagerInterface, DatabaseManager)
        provider.register(MigrationInterface, CryptoMigration)
        provider.register(MigrationInterface, AlertMigration)
        provider.register(ListenerInterface[SymbolUpdateEvent], AlertManager)
        provider.register(AlertManagerInterface, AlertManager)
        provider.register(DisplayInterface, Discord)
        provider.register(LogInterface, ConsoleLog)
        service_collection.add_provider(provider)
