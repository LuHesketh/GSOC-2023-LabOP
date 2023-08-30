from typing import Optional

import serial # type: ignore

from pylabrobot.pumps.backend import PumpBackend
    


class STARDEVICE(HeatShakerBackend):
  """ CONCRETE Backend for the STAR heater shaker. This will essencially take the role of the machine by making use of the firmware strings  """

  def __init__(self, node:  (int [1,8])):
    self.node = node
    self.ser: Optional[serial.Serial] = None


  async def CreateStarDevice(self,deviceNumber: int, node: (int [1,8])):
    self.ser = serial.Serial(ML_Star=deviceNumber, node = 1)

    self.send_command("T1QU")
    self.send_command("T1QW")
    self.send_command("T1RF")


  def send_command(self, command: str):
    assert self.ser is not None
    command = "\x02" + command + "\x0d"
    self.ser.write(command.encode())
    return self.ser.read()

  def StartTempCtrl(self, node: int):
    cmd = f"T1TAta0370tb1800tc0020td0060"
    self.send_command(cmd)


  def run_continuously(self, speed: float):
    if speed == 0:
      self.halt()
      return

    direction = "+" if speed > 0 else "-"
    speed = int(abs(speed))
    cmd = f"P21S{direction}{speed}G0"
    self.send_command(cmd)

  def halt(self):
    self.send_command("P21H")

  def StartShakerTimed(self, node: int):    