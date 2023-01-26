from .gadget import Gadget
from .midi_controller import MIDIController
from .robot import Robot
from .phone import Phone
from src.utils.data import load_pickle, dump_pickle
import logging
logging.basicConfig(
    # filename='example.log',
    encoding='utf-8',
    level=logging.INFO,
    )

