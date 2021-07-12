from holobot.framework.ioc import ServiceCollection, ServiceDiscovery
from holobot.sdk import KernelInterface
from holobot.sdk.ioc.models import ExportMetadata
from typing import Tuple

import asyncio

class DependencyResolver:
	def __init__(self, exports: Tuple[ExportMetadata, ...]) -> None:
		pass

if __name__ == "__main__":
		event_loop = asyncio.get_event_loop()
		service_collection = ServiceCollection()
		# The idea here is to register the services for each extension independently,
		# however, today it doesn't make sense as they're still in the same package.
		# Therefore, for now we just register everything from the entire package.
		exports = ServiceDiscovery.get_exports("holobot")
		service_collection.get(KernelInterface).run()
