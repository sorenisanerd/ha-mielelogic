from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MACHINE_COLOR_IN_USE,
    MACHINE_SYMBOL_DRYER,
    MACHINE_SYMBOL_WASHER,
    MACHINE_TYPE_DRYER,
    MACHINE_TYPE_WASHER,
    STATE_AVAILABLE,
    STATE_NOT_AVAILABLE,
)
from .coordinator import MieleLogicCoordinator

MACHINE_ICONS = {
    MACHINE_TYPE_WASHER: "mdi:washing-machine",
    MACHINE_TYPE_DRYER: "mdi:tumble-dryer",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MieleLogicCoordinator = hass.data[DOMAIN][entry.entry_id]
    machines = coordinator.data.get("MachineStates", [])
    async_add_entities(
        MieleLogicMachineSensor(coordinator, entry, machine) for machine in machines
    )


class MieleLogicMachineSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MieleLogicCoordinator,
        entry: ConfigEntry,
        machine: dict,
    ) -> None:
        super().__init__(coordinator)
        self._unit_name: str = machine["UnitName"]
        self._attr_unique_id = f"{entry.entry_id}_{self._unit_name}"
        self._attr_name = self._unit_name

        symbol = machine.get("MachineSymbol")
        if symbol == MACHINE_SYMBOL_WASHER:
            self._machine_type = MACHINE_TYPE_WASHER
        elif symbol == MACHINE_SYMBOL_DRYER:
            self._machine_type = MACHINE_TYPE_DRYER
        else:
            self._machine_type = f"machine_{symbol}"

        self._attr_icon = MACHINE_ICONS.get(self._machine_type, "mdi:washing-machine")

    @property
    def _machine_data(self) -> dict | None:
        if not self.coordinator.data:
            return None
        for machine in self.coordinator.data.get("MachineStates", []):
            if machine["UnitName"] == self._unit_name:
                return machine
        return None

    @property
    def native_value(self) -> str | None:
        machine = self._machine_data
        if machine is None:
            return None
        return STATE_NOT_AVAILABLE if machine.get("MachineColor") == MACHINE_COLOR_IN_USE else STATE_AVAILABLE

    @property
    def extra_state_attributes(self) -> dict:
        machine = self._machine_data
        if machine is None:
            return {}
        status = f"{machine.get('Text1', '').strip()} {machine.get('Text2', '').strip()}".strip()
        return {
            "machine_type": self._machine_type,
            "status": status,
        }
