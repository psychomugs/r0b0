from abc import abstractmethod
import pickle
import logging

logger = logging.getLogger(__name__)
import datetime


class Cable(object):
    def __init__(
        self,
    ):
        self.input_event = ""

    def log_data(func, *args, **kwargs):
        def log_func(self, *args, **kwargs):
            # logging.debug(datetime.datetime.now())
            # logging.debug('LOG_DATA')
            # logging.debug(args)
            # logging.debug(kwargs)
            # logging.debug(self.__class__)
            return func(self, *args, **kwargs)

        return log_func
        # if 'data' in kwargs:
        # logging.debug()

    # @abstractmetod
    @log_data
    def __call__(self, data: dict):
        """
        When the Cable is called, it will convert an input dictionary into an output dictionary

        :param data: _description_
        :return: _description_
        """
        logging.debug(f"LOG_DATA {datetime.datetime.now()}")
        # logging.debug(args)
        # logging.debug(kwa rgs)
        logging.debug(self.__class__)
        logging.debug(data)
        # return self.inner_call(data)

    @abstractmethod
    def inner_call(self, *args, **kwargs):
        return {}


# class TapeCable(Cable):
#     """
#     Helper class for "echoing"
#     """
#     def __init__(self):
#         self.input_event = "tape"

#     def __call__(self, data):
#         super().__call__(data)
#         event = data["event"]
#         return {
#             "event":event,
#             "data":
#         }


class Key2MouseCable(Cable):
    """
    Converts key presses to absolute mouse positions
    """

    def __init__(
        self,
    ):
        self.input_event = "keydown"

    # @Cable.log_data
    def __call__(self, data):
        super().__call__(data)

        # def inner_call(self, data):
        key2pos_dict = {
            "q": [100, 100],
            "w": [500, 100],
            "e": [900, 100],
            "a": [100, 400],
            "s": [500, 400],
            "d": [900, 400],
            "z": [100, 700],
            "x": [500, 700],
            "c": [900, 700],
        }
        # key2pos_dict.setdefault([500,400])
        [x, y] = key2pos_dict.get(data["unicode"], [500, 400])
        # print(x,y)
        # logger.debug(f"{x}, {y}")
        return {
            "event": "mouse_place",
            "x": x,
            "y": y,
        }


class Key2TimeModeCable(Cable):
    """
    Converts key presses to absolute mouse positions
    """

    def __init__(
        self,
    ):
        self.input_event = "keydown"

    def __call__(self, data):
        key2mode = {
            "q": "idle",
            "w": "stopwatch",
            "e": "timer",
        }
        mode = key2mode.get(data["unicode"], "idle")
        # key2pos_dict.setdefault([500,400])
        return {"event": "set_mode", "mode": mode}


class MidiRel2PositionCable(Cable):
    """
    Converts relative MIDI_CC messages (increment/decrement) into relative motor positions
    for OpenArm
    """

    def __init__(
        self,
    ):
        self.input_event = "midi_cc"

    def __call__(self, data):
        msg = pickle.loads(data["msg"])

        # Map increment (1) / decrement (127)
        value_dict = {1: 1, 127: -1}
        # Scale the values for each motor
        scale_dict = {1: 600, 2: 600, 3: 600, 4: 300}  # Rotate the wrist less
        value_scale = scale_dict.get(msg.control, 300)
        value_dict.setdefault(0)

        return {
            "event": "position",
            "value": value_dict.get(msg.value, 0) * value_scale,
            "motor_id": msg.control,
            "absolute": False,
        }


class MIDI2MicCable(Cable):
    def __init__(self):
        self.input_event = "midi_on"

    def __call__(self, data):
        return {"event": "listen"}

class MIDI2ControlVecCable(Cable):
    def __init__(self):
        self.input_event = "midi_cc"
        self.min_len = 10
        self.max_len = 60
        self.min_temp = 0.5
        self.max_temp = 1.5
        self.vector_range = [-2, 2]
        self.len_range = [10, 60]
        self.temp_range = [0.5, 1.5]
        self.rep_range = [0.8, 1.3]
        self.cc_range = [0,127]
    
    def _map_range(self, input_range, output_range, value):
        return (value / (input_range[1] - input_range[0])) \
            * (output_range[1] - output_range[0]) \
                + output_range[0]


    def __call__(self, data):
        # msg = pickle.loads(data["msg"])
        # print(data)
        # breakpoint()
        # msg = data['msg']

        # cc = msg.control
        # logging.warning(data)
        # TODO -
        # 
        # Ignore if not on first channel (0)
        # if data["channel"] != 0:
            # return

        cc = data['value']
        
        event = None
        match data['control']:
            case 1:
                event = "vector"
                output_range = self.vector_range
            case 2:
                event = "max_len"
                output_range = self.len_range
            case 3:
                event = "temperature"
                output_range = self.temp_range
            case 4:
                event = "repetition_penalty"
                output_range = self.rep_range
            case _:
                return 
        value = self._map_range(self.cc_range, output_range, cc)

        # if data['channel'] == 0 and data['control']==1:
            # logging.warning(f"MIDI_CC: {cc}")
        return {
            "event": event,
            "value": value,
        }

class Wav2MotorCable(Cable):
    def __init__(self):
        self.input_event = "wav"

    def __call__(self, data):
        # Will be float normalized between 0.-1.
        wav_value = data["value"]
        motor_value = int(wav_value * 1000 + 200)
        # logging.info(motor_value)
        return {
            "event": "position",
            "value": motor_value,
            "motor_id": 1,
            "absolute": True,
        }


class Ser2MicCable(Cable):
    def __init__(self):
        self.input_event = "serial"

    def __call__(self, data):
        super().__call__(data)
        if data["detected"]:
            return {
                "event": "listen",
            }


class Response2ListenCable(Cable):
    def __init__(self):
        self.input_event = "response"

    def __call__(self, data):
        super().__call__(data)
        return [
            {"event": "write", "text": data["text"]},

            # {
            #     "event": "listen",
            # },
        ]
