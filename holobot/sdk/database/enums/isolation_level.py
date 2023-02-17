from enum import IntEnum, unique

@unique
class IsolationLevel(IntEnum):
    """Defines the valid values for a transaction's isolation level."""

    READ_COMMITTED = 0
    """Each consistent read, even within the same transaction,
    sets and reads its own fresh snapshot.
    """

    SERIALIZABLE = 1
    """Emulates serial transaction execution for all committed transactions;
    as if transactions had been executed one after another,
    serially, rather than concurrently.
    """
