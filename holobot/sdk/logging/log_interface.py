from .enums import LogLevel
from typing import Optional

class LogInterface:
    """Interface for a service used for writing logs.

    Where the logs appear depend on the implementation of the interface
    (such as the terminal or a file).
    """
    
    @property
    def name(self) -> Optional[str]:
        """Gets the name of the logger."""
        return self.__name
    
    @name.setter
    def name(self, value: Optional[str]) -> None:
        """Sets the name of the logger."""
        self.__name = value

    @property
    def log_level(self) -> LogLevel:
        """Gets the log level."""

        return self.__log_level
    
    @log_level.setter
    def log_level(self, value: LogLevel):
        """Sets the log level."""

        self.__log_level = value
    
    def set_global_log_level(self, log_level: LogLevel):
        """Sets the log level for the entire logger tree.

        Walks back up till the root logger through the child tree
        and recursively sets the log level for it and all of its children.

        Parameters
        ----------
        log_level : LogLevel
            The new log level to be set.
        """
        
        raise NotImplementedError

    def with_name(self, module: str, name: str) -> 'LogInterface':
        """Gets or creates a logger instance for a specific name.

        The name of the logger is automatically included in the logs.
        A typical usage would be to create independent loggers for
        independent classes so that their name is included in the
        logs automatically which helps identify where each message
        comes from.

        Parameters
        ----------
        module : str
            The name of the owning module that is going to use the logger.
        
        name : str
            The name of the logger, typically the class/file name.
        
        Returns
        -------
        LogInterface
            An instance of the logger for the specified name.
        """

        raise NotImplementedError

    def write(self, level: LogLevel, message: str, error: Optional[Exception] = None) -> None:
        """Creates a new log entry.

        Writes the specified message to the logs
        using the specified log level
        and adding information about the optional error.

        Parameters
        ----------
        level : LogLevel
            The log level at which to write the entry.
        
        message : str
            The message to be written.
        
        error : Exception, optional
            An optional error to be included.
        """

        raise NotImplementedError

    def trace(self, message: str) -> None:
        """Shorthand for ``write`` with trace level."""
        self.write(LogLevel.TRACE, message)

    def debug(self, message: str) -> None:
        """Shorthand for ``write`` with debug level."""
        self.write(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        """Shorthand for ``write`` with information level."""
        self.write(LogLevel.INFORMATION, message)

    def warning(self, message: str) -> None:
        """Shorthand for ``write`` with warning level."""
        self.write(LogLevel.WARNING, message)

    def error(self, message: str, error: Optional[Exception] = None) -> None:
        """Shorthand for ``write`` with error level."""
        self.write(LogLevel.ERROR, message, error)

    def critical(self, message: str, error: Exception) -> None:
        """Shorthand for ``write`` with critical level."""
        self.write(LogLevel.CRITICAL, message, error)
