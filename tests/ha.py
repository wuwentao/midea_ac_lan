"""Version-compatible imports for Home Assistant's shared test harness."""

try:
    from pytest_homeassistant.common import MockConfigEntry
except ImportError:
    from pytest_homeassistant_custom_component.common import MockConfigEntry

__all__ = ["MockConfigEntry"]
