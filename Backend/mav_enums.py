# The below class is the Enums for MAV_RESULTS in the fields of "COMMAND_ACK" (https://mavlink.io/en/messages/common.html#COMMAND_ACK)
class CommandResults:
    MAV_RESULT_ACCEPTED = 0
    MAV_RESULT_TEMPORARILY_REJECTED = 1
    MAV_RESULT_DENIED = 2
    MAV_RESULT_UNSUPPORTED = 3
    MAV_RESULT_FAILED = 4
    MAV_RESULT_IN_PROGRESS = 5
    MAV_RESULT_CANCELLED = 6
    MAV_RESULT_COMMAND_LONG_ONLY = 7
    MAV_RESULT_COMMAND_INT_ONLY = 8
    MAV_RESULT_COMMAND_UNSUPPORTED_MAV_FRAME = 9


class MUASCommands:
    WADJET = 975
    LIFELINE = 976


class WadjetCommands:
    NEUTRAL_MODE = 0
    TRACK_GPS_MODE = 1
    TRACK_TARGET_MODE = 2
    RESET_POSITION = 3


class LifelineCommands:
    DRIP = 0
    SMERF = 1
    NERF = 2


class MUASComponentID:
    WADJET = 169
    VISION = 170
    LIFELINE = 171
    MISSION_MANAGEMENT = 172


class LifelineCommandResults: 
    DOOR_OPENING = 310
    DOOR_OPENING_SUCCESS = 311
    DOOR_OPENING_FAILED = 312

    DOOR_CLOSING = 510
    DOOR_CLOSING_SUCCESS = 511
    DOOR_CLOSING_FAILED = 512
    

class LifelineState:
    # defining state constants
    LOADING = 100
    IDLE = 200
    LOWERING = 300
    RELEASING = 400
    RAISING = 500
    EMERGENCY = 900
    NERF = 800

    LifeLineStateDict = {
        # defining state constants
        "100": "LOADING",
        "200": "IDLE",
        "300": "LOWERING",
        "400": "RELEASING",
        "500": "RAISING",
        "900": "EMERGENCY",
        "800": "NERF",
    }
    #CommandResults(msg.result).name
    #E.g LifelineState(100).name


