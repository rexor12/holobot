from holobot.framework import Kernel
from holobot.framework.ioc import DependencyResolver, ServiceDiscovery
from holobot.framework.ioc.graphs.exceptions import CyclicGraphError

if __name__ == "__main__":
	# The idea here is to register the services for each extension independently,
	# however, today it doesn't make sense as they're still in the same package.
	# Therefore, for now we just register everything from the entire package.
	exports = ServiceDiscovery.get_exports("holobot")
	resolver = DependencyResolver(exports)
	try:
		resolver.resolve(Kernel).run()
	except CyclicGraphError as error:
		print("Failed to resolve the services, because there is a cycle in the dependency graph. Nodes: {}".format(
			", ".join([str(node) for node in error.nodes])
		))
