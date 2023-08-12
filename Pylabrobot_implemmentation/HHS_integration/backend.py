from __future__ import annotations

from abc import ABC, abstractmethod
import sys
from typing import List, Optional, Type

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class HamiltonHeatShaker(HeatShakerBackend):
    """An abstract class for on deck Heater Shaker. wrapping up the commands in async functions that will be called
    during the robot script"""

    @abstractmethod
    async def initialize(self, initializeAlways) -> None:
        "initialize the Heater Shaker"

    self._send_command("TODO")

    @abstractmethod
    async def Create_STAR_Device(self, starDevice, usedNode: float) -> None:
        "Create the heater shaker"

    self._send_command("TODO")

    @abstractmethod
    async def Begin_Monitoring(
        self,
        deviceNumber: float,
        shakingToleranceRange: float,
        sampleInterval: float,
        action: float,
    ) -> None:
        "Begin monitoring the heater shaker"

    self._send_command("TODO")

    @abstractmethod
    async def StartShaker(self, deviceNumber: float, shakingSpeed: float) -> None:
        "Start the heater shaker"

    self._send_command("TODO")

    # serialization

    def serialize(self):
        """Serialize the backend so that an equivalent backend can be created by passing the dict
        as kwargs to the initializer. The dict must contain a key "type" that specifies the type of
        backend to create. This key will be removed from the dict before passing it to the initializer.
        """

        return {
            "type": self.__class__.__name__,
        }

    @classmethod
    def deserialize(cls, data: dict) -> HeatShakerBackend:
        """Deserialize the backend. Unless a custom serialization method is implemented, this method
        should not be overridden."""

        # Recursively find a subclass with the correct name
        def find_subclass(
            cls: Type[HeatShakerBackend], name: str
        ) -> Optional[Type[HeatShakerBackend]]:
            if cls.__name__ == name:
                return cls
            for subclass in cls.__subclasses__():
                subclass_ = find_subclass(subclass, name)
                if subclass_ is not None:
                    return subclass_
            return None

        subclass = find_subclass(cls, data["type"])
        if subclass is None:
            raise ValueError(f"Could not find subclass with name {data['type']}")

        del data["type"]
        return subclass(**data)
