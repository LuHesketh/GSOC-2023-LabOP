from typing import Optional

import serial # type: ignore

from GSOC-2023-LabOP.HHS_integration import abstract_backend
    


class STARDEVICE(HeatShakerBackend):
  """ CONCRETE Backend for the STAR heater shaker. This will essencially take the role of the machine by making use of the firmware strings  """

  def __init__(self, node:(int [1,8])):
    self.node = node
    self.ser: Optional[serial.Serial] = None
  
  def send_command(self, command: str):
    assert self.ser is not None
    command = "\x02" + command + "\x0d"
    self.ser.write(command.encode())
    return self.ser.read()


  async def CreateStarDevice(self, node):
    self.ser = serial.Serial(ML_Star= "ML_Star", node = 1)
    ML_Star= "ML_Star"
    node = 1
    cmd =f"T1QU"
    cmd =f"T1QW"
    cmd =f"T1RF"
    self.send_command(cmd)

  async def StartTempCtrl(self, temp:float, wait_for_temp_reached:int)
    temp = (float [0.0, 105.0])
    temp
    wait_for_temp_reached
    cmd = f"T1TAta0370tb1800tc0020td0060"
    self.send_command(cmd)
  
  async def StartShakerTimed(self, shakingSpeed: float, shakingTime: float)
    shakingSpeed = (int [30, 2500])
    shakingTime = (int [1, 30000])
    shakingSpeed
    shakingTime
    cmd = f"T1LPlp1"
    cmd = f"T1STsd00060st0sv0560sr01000" 
    self.send_command(cmd)
  
    self.send_command
  
  async def WaitForShaker(self):##need to double check
    cmd = f"T1SW"
    cmd = f"T1LPlp0"

    self.send_command(cmd)
  
  async def StopTempCtrl(self):##need to double check
    cmd = f"T1TO"

    self.send_command(cmd)
  
  async def Terminate(self):##need to double check
    self.send_command

