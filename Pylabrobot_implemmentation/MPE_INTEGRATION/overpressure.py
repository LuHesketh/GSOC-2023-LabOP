import asyncio

from pylabrobot.resources import Cos_96_EZWash, Coordinate, STARLetDeck
from GSOC-2023-LabOP.MPE_INTEGRATION import MPEbackend
from GSOC-2023-LabOP.MPE_INTEGRATION import MPEbackend

from GSOC-2023-LabOP.MPE_INTEGRATION import MPE
from GSOC-2023-LabOP.MPE_INTEGRATION import MPE

backend =MPEbackend()
MPE = MPE(backend=backend, deck=STARLetDeck())
deck=STARLetDeck()


async def __init__():
  await MPE.setup()

#assign the MPE plate
MPE_plate = Cos_96_EZWash(name="MPE_plate")

#provide information necessary for protocol

comPort = 12
BaudRate = 921600
SimulationMode = 0
options = 0
FilterHeight = 14.9
NozzleHeight = 14.9

ControlPoints = "pressure, 0, 5;pressure, 10, 5;pressure, 15, 5;pressure, 20, 5;pressure, 30, 5;pressure, 40, 5;pressure, 50, 5; pressure, 60, 5"
ReturnPlateToIntegrationArea = 1
WasteContainerID = 0
DisableVacuumCheck = 1



async def MPE_overpressure():
  MPE.mpe2_connect_com(self, 1, comPort, BaudRate, SimulationMode, options)
  MPE.mpe2_Initialize(self, 1)
  MPE.mpe2_FilterPlatePlaced(self, 1, FilterHeight, NozzleHeight)
  MPE.mpe2_ProcessFilterToWasteContainer(self, 1, ControlPoints,ReturnPlateToIntegrationArea, WasteContainerID, DisableVacuumCheck)
  MPE.mpe2_FilterPlateRemoved(self, 1) 

asyncio .run(__init__())
asyncio .run(MPE_overpressure())