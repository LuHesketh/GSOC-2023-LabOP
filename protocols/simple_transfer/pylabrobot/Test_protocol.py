import pylabrobot

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends import STAR
from pylabrobot.resources.hamilton import STARLetDeck
backend = STAR()
from pylabrobot import LiquidHandler
from pylabrobot.liquid_handling.backends import STAR
from pylabrobot.resources import Deck

deck = Deck.load_from_json_file("hamilton-layout.json")
lh = LiquidHandler(backend=STAR(), deck=deck)
await lh.setup()

await lh.pick_up_tips(lh.get_resource("tip_rack")["A1"])
await lh.aspirate(lh.get_resource("plate")["A1"], vols=100)
await lh.dispense(lh.get_resource("plate")["A2"], vols=100)
await lh.return_tips()

