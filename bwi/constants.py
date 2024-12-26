from enum import StrEnum


class ItemDecision(StrEnum):
    KEEP_ITEM = "behalten"
    DISCARD_ITEM = "wegwerfen"
    GIVE_AWAY = "verschenken"
    UNDECIDED = "unentschlossen"
