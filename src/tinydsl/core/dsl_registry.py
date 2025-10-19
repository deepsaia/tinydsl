"""
DSL Registry - Plugin architecture for dynamic DSL discovery and registration.

Allows users to register custom DSLs at runtime and query available DSLs.
"""

from typing import Dict, Type, List, Optional
from tinydsl.core.base_dsl import BaseDSL


class DSLRegistry:
    """
    Central registry for all available DSLs.

    Supports:
    - Dynamic registration of DSL classes
    - Discovery of available DSLs
    - Instantiation of DSLs by name
    """

    def __init__(self):
        self._registry: Dict[str, Type[BaseDSL]] = {}

    def register(self, name: str, dsl_class: Type[BaseDSL]) -> None:
        """
        Register a DSL class.

        Args:
            name: Unique identifier for the DSL
            dsl_class: Class implementing BaseDSL

        Raises:
            ValueError: If DSL doesn't inherit from BaseDSL or name already registered
        """
        if not issubclass(dsl_class, BaseDSL):
            raise ValueError(f"{dsl_class} must inherit from BaseDSL")

        if name in self._registry:
            raise ValueError(f"DSL '{name}' is already registered")

        self._registry[name] = dsl_class

    def unregister(self, name: str) -> None:
        """Remove a DSL from the registry."""
        if name in self._registry:
            del self._registry[name]

    def get(self, name: str) -> Optional[Type[BaseDSL]]:
        """Get a DSL class by name."""
        return self._registry.get(name)

    def create(self, name: str, **kwargs) -> BaseDSL:
        """
        Instantiate a DSL by name.

        Args:
            name: DSL identifier
            **kwargs: Configuration passed to DSL constructor

        Returns:
            Instantiated DSL object

        Raises:
            KeyError: If DSL name not found
        """
        dsl_class = self._registry.get(name)
        if dsl_class is None:
            raise KeyError(f"DSL '{name}' not found in registry")
        return dsl_class(**kwargs)

    def list_dsls(self) -> List[str]:
        """List all registered DSL names."""
        return list(self._registry.keys())

    def list_all(self) -> Dict[str, Type[BaseDSL]]:
        """Get all registered DSLs."""
        return self._registry.copy()

    def __contains__(self, name: str) -> bool:
        """Check if DSL is registered."""
        return name in self._registry

    def __repr__(self) -> str:
        dsls = ", ".join(self._registry.keys())
        return f"<DSLRegistry: {dsls}>"


# Global registry instance
_global_registry = DSLRegistry()


def register_dsl(name: str, dsl_class: Type[BaseDSL]) -> None:
    """Register a DSL in the global registry."""
    _global_registry.register(name, dsl_class)


def get_dsl(name: str) -> Optional[Type[BaseDSL]]:
    """Get a DSL class from the global registry."""
    return _global_registry.get(name)


def create_dsl(name: str, **kwargs) -> BaseDSL:
    """Create a DSL instance from the global registry."""
    return _global_registry.create(name, **kwargs)


def list_available_dsls() -> List[str]:
    """List all available DSLs in the global registry."""
    return _global_registry.list_dsls()


def get_registry() -> DSLRegistry:
    """Get the global DSL registry."""
    return _global_registry
