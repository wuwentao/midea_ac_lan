"""Temperature members shared by the climate and water heater entities.

HA 2026.11 added the ``native_*`` temperature members and deprecated the old names
(scheduled for removal in HA 2027.11). Entities implement the ``native_*`` names only.
Older HA versions still read the old names, so below 2026.11 this mixin forwards them.
"""

from typing import cast

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION

if (MAJOR_VERSION, MINOR_VERSION) >= (2026, 11):

    class NativeTemperatureCompat:
        """Nothing to forward: HA 2026.11+ reads the native_* members directly."""

else:

    class NativeTemperatureCompat:  # type: ignore[no-redef]
        """Forward the native_* temperature members to the names HA < 2026.11 reads."""

        _attr_native_temperature_unit: str
        _attr_native_target_temperature_high: float | None
        _attr_native_target_temperature_low: float | None

        @property
        def native_temperature_unit(self) -> str:
            """Native temperature unit."""
            return self._attr_native_temperature_unit

        @property
        def native_target_temperature_high(self) -> float | None:
            """Native high end of the target temperature range."""
            return self._attr_native_target_temperature_high

        @property
        def native_target_temperature_low(self) -> float | None:
            """Native low end of the target temperature range."""
            return self._attr_native_target_temperature_low

        @property
        def temperature_unit(self) -> str:
            """Native temperature unit."""
            return self.native_temperature_unit

        @property
        def current_temperature(self) -> float | None:
            """Native current temperature."""
            return cast("float | None", self.native_current_temperature)  # type: ignore[attr-defined] # pylint: disable=no-member

        @property
        def target_temperature(self) -> float | None:
            """Native target temperature."""
            return cast("float | None", self.native_target_temperature)  # type: ignore[attr-defined] # pylint: disable=no-member

        @property
        def target_temperature_high(self) -> float | None:
            """Native high end of the target temperature range."""
            return self.native_target_temperature_high

        @property
        def target_temperature_low(self) -> float | None:
            """Native low end of the target temperature range."""
            return self.native_target_temperature_low
