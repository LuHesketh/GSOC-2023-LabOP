from typing import Optional

import serial # type: ignore

from GSOC-2023-LabOP.MPE_INTEGRATION import abstract_backend


class MPE(MPEBackend):
  """ CONCRETE Backend for the MPE pressure pump. This will essencially take the role of the machine by making use of the firmware strings  """

  def __init__(self, deviceId:(int [1,8])):
    self.deviceId = deviceId
    self.ser: Optional[serial.Serial] = None
  
  def send_command(self, command: str):
    assert self.ser is not None
    command = "\x02" + command + "\x0d"
    self.ser.write(command.encode())
    return self.ser.read()

  async def  ConnectUsingCOM(self, deviceId: int, comPort: str, BaudRate: str , SimulationMode: bool, options: int)
    ComPort = str
    BaudRate = str
    SimulationMode = str
    options = int 

    self.send_command

  async def  Initialize(self, deviceId: int)   
    self.send_command

  async def  FilterPlatePlaced(self, deviceId: int, FilterHeight: float, NozzleHeight: float)
    FilterHeight = float
    NozzleHeight = float

    self.send_command

  async def  FilterPlateRemoved(self, deviceId: int)
    self.send_command

  async def  ProcessFilterToWasteContainer(self, deviceId: int, ControlPoints: str,ReturnPlateToIntegrationArea: bool, WasteContainerID: int, DisableVacuumCheck: bool)
    ControlPoints = str
    ReturnPlateToIntegrationArea = bool
    WasteContainerID = int 
    DisableVacuumCheck = bool
    self.send_command

  async def  mpe2_RetrieveFilterPlate(self, deviceId: int)
    self.send_command



  







