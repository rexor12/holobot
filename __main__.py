from holobot.framework import Kernel
from kanata import InjectableCatalog, LifetimeScope, find_injectables
from kanata.graphs.exceptions import CyclicGraphException

import structlog

if __name__ == "__main__":
    # TODO Temporarily disabled, incorporate structlog later.
    structlog.configure_once(logger_factory=structlog.ReturnLoggerFactory())
    
    # The idea here is to register the services for each extension independently,
    # however, today it doesn't make sense as they're still in the same package.
    # Therefore, for now we just register everything from the entire package.
    registrations = find_injectables("holobot")
    catalog = InjectableCatalog(registrations)
    scope = LifetimeScope(catalog)
    try:
        scope.resolve(Kernel).run()
    except CyclicGraphException as error:
        print((
            'Failed to resolve the services, because there is a cycle in the dependency graph.'
            f' Nodes: {", ".join([str(node) for node in error.nodes])}'
        ))
