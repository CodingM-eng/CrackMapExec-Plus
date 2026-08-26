"""Custom exception hierarchy for CrackMapExec+."""


class CMEPlusError(Exception):
    """Base exception for all CrackMapExec+ errors."""


class TargetParseError(CMEPlusError):
    """Raised when a target specification or file cannot be parsed."""

    def __init__(self, message: str, raw_input: str | None = None, line_number: int | None = None):
        super().__init__(message)
        self.raw_input = raw_input
        self.line_number = line_number


class ProtocolError(CMEPlusError):
    """Raised when a protocol encounter errors or is unsupported."""


class ProtocolNotImplementedError(ProtocolError):
    """Raised when a requested protocol capability is not yet implemented."""


class ModuleError(CMEPlusError):
    """Raised when a module fails to load or execute."""


class ConfigurationError(CMEPlusError):
    """Raised when configuration loading or validation fails."""


class JobExecutionError(CMEPlusError):
    """Raised during job queue execution failures."""


class VideoCatalogError(CMEPlusError):
    """Raised when video guide catalog operations fail."""


class ProjectBatchError(CMEPlusError):
    """Raised when batch project YAML parsing or validation fails."""
