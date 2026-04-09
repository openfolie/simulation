from enum import Enum, auto


# If we ever wish the enum values should be strings, then replace
# the inherited class from "Enum" to "StrEnum"
class Material(Enum):
    SAND = auto()
    DIRT = auto()
    WOOD = auto()
    COAL = auto()
    IRON = auto()
    GOLD = auto()
    # This is a test list, there will obviously be much more stuff

    COUNT = auto()
