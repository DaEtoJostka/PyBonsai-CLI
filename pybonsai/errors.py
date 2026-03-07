"""Library-specific exceptions."""


class PyBonsaiError(Exception):
    """Base exception for PyBonsai."""


class ConfigurationError(PyBonsaiError):
    """Raised when CLI or Python configuration is invalid."""


class RadioError(PyBonsaiError):
    """Raised when radio playback fails."""
