from __future__ import annotations

from abc import ABC, abstractmethod
import sys
from typing import List, Optional, Type

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class HeatShakerBackend(ABC):
    """An abstract class for on the HAMILTON on deck Heater Shaker."""

    async def __init__(self):
        self.setup_finished = False

    async def setup(self):
        self.setup_finished = True

    async def stop(self):
        self.setup_finished = False
  

    @abstractmethod
    async def HHS_CreateStarDevice(self, starDevice: str, ML_Star node: (int [1,2])) -> None:
        "Creates the heater shaker"


    @abstractmethod
    async def HHS_BeginMonitoring(
        self,
        deviceNumber: int,
        shakingToleranceRange: int,
        sampleInterval: int,
        action: int,
    ) -> None:
        "Begin monitoring the heater shaker"
w


    @abstractmethod
    async def _send_command(self) -> None:
    
    @abstractmethod
    async def HHS_CreateUSBDevice(self, ML_Star node: (int [1,8])) -> None:

    @abstractmethod
    async def HHS_StartShaker(self, deviceNumber: int, shakingSpeed: (int [30, 2500])) -> None:
        "Starts the heater shaker"

    @abstractmethod
    async def HHS_StartShaker_timed(self, deviceNumber: int, shakingSpeed: (int [30, 2500]), shakingTime: (int [1, 30000])) -> None:

    @abstractmethod
    async def HHS_StartTempCtrl(self, deviceNumber: int) -> None:
    
    @abstractmethod
    async def HHS_WaitForTempCtrl(self, deviceNumber: int) -> None:

    @abstractmethod
    async def HHS_WaitForShaker(self, deviceNumber: int, temperature:(float [0.0, 105.0]), waitForTempReached:((Int) -> Bool)) -> None:

    @abstractmethod
    async def HHS_StopTempCtrl(self, deviceNumber: int) -> None:

    @abstractmethod
    async def HHS_Terminate(self, deviceNumber: int) -> None:
    
  




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
