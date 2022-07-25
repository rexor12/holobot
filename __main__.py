import logging

import structlog

from kanata import InjectableCatalog, LifetimeScope, find_injectables
from kanata.graphs.exceptions import CyclicGraphException

from holobot.framework import Kernel

if __name__ == "__main__":

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper("iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )

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
