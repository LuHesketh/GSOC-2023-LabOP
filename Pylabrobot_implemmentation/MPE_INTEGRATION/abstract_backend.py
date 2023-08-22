from __future__ import annotations

from abc import ABC, abstractmethod
import sys
from typing import List, Optional, Type

if sys.version_info >= (3, 8):
  from typing import Literal
else:
  from typing_extensions import Literal

class MPEbackend(ABC):
  """ An abstract class for a plate reader. Plate readers are devices that can read luminescence,
  absorbance, or fluorescence from a plate. """

  async def __init__(self):
        self.setup_finished = False

    async def setup(self):
        self.setup_finished = True

    async def stop(self):
        self.setup_finished = False

  @abstractmethod
  async def  mpe2_connect_com(self, deviceId: int, comPort: int, BaudRate: int , SimulationMode: bool, options: int) -> None:
    """ connects MPE via com ports"""

  @abstractmethod
  async def  mpe2_Initialize(self, deviceId: int) -> None:
    """ initialize MPE """
  
  @abstractmethod
  async def  mpe2_FilterPlatePlaced(self, deviceId: int, FilterHeight: float, NozzleHeight: float) -> None:
    """ instanciates that a filter plate has been placed at the MPE deck """

  @abstractmethod
  async def  mpe2_FilterPlateRemoved(self, deviceId: int) -> None:
    """instanciates that a filter plate has been removed from the MPE deck  """


  @abstractmethod
  async def  mpe2_ClampFilterPlate(self, deviceId: int) -> None:
    """ command for the MPE deck to clamp plate that has been placed """

  @abstractmethod
  async def  mpe2_RetrieveFilterPlate(self, deviceId: int) -> None:
    """ retrieves filter plate back to deck for next operation"""
  
  @abstractmethod
  async def  mpe2_Disconnect(self, deviceId: int) -> None:
    """ disconnects MPE2"""

  @abstractmethod
  async def  mpe2_ProcessFilterToWasteContainer(self, deviceId: int, ControlPoints: str,ReturnPlateToIntegrationArea: bool, WasteContainerID: int, DisableVacuumCheck: bool) -> None:
    """ activates MPE air pump and processes filter plate contents through filters"""

  @abstractmethod
  async def  mpe2_CollectionPlatePlaced(self, deviceId: int, CollectionPlateHeight: float, OffsetFromNozzles: float) -> None:
    """ disconnects MPE2"""


  # Copied from liquid_handling/backend.py.

  def serialize(self):
    """ Serialize the backend so that an equivalent backend can be created by passing the dict
    as kwargs to the initializer. The dict must contain a key "type" that specifies the type of
    backend to create. This key will be removed from the dict before passing it to the initializer.
    """

    return {
      "type": self.__class__.__name__,
    }

  @classmethod
  def deserialize(cls, data: dict) -> MPEbackend:
    """ Deserialize the backend. Unless a custom serialization method is implemented, this method
    should not be overridden. """

    # Recursively find a subclass with the correct name
    def find_subclass(cls: Type[MPEbackend], name: str) -> \
      Optional[Type[MPEbackend]]:
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
