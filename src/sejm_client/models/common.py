from enum import Enum


class BillStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WITHDRAWN = "WITHDRAWN"
    NOT_PROCEEDED = "NOT_PROCEEDED"
    OBSOLETE = "OBSOLETE"
    ADOPTED = "ADOPTED"


class BillType(str, Enum):
    BILL = "BILL"
    DRAFT_RESOLUTION = "DRAFT_RESOLUTION"
    BILL_AMENDMENT = "BILL_AMENDMENT"
    RESOLUTION_AMENDMENT = "RESOLUTION_AMENDMENT"


class ApplicantType(str, Enum):
    DEPUTIES = "DEPUTIES"
    COMMITTEE = "COMMITTEE"
    GOVERNMENT = "GOVERNMENT"
    PRESIDIUM = "PRESIDIUM"
    PRESIDENT = "PRESIDENT"
    SENATE = "SENATE"
    CITIZENS = "CITIZENS"


class UrgencyStatus(str, Enum):
    NORMAL = "NORMAL"
    URGENT = "URGENT"


class ActStatus(str, Enum):
    BINDING = "obowiązujący"
    REPEALED = "uchylony"
    EXPIRED = "wygasły"
    NOT_IN_FORCE = "nieobowiązujący"
    DEEMED_REPEALED = "uznany za uchylony"
    ACT_EXPIRED = "wygaśnięcie aktu"
    CONSOLIDATED = "akt posiada tekst jednolity"
    COVERED_BY_CONSOLIDATED = "akt objęty tekstem jednolitym"
    ONE_TIME = "akt jednorazowy"
    INDIVIDUAL = "akt indywidualny"
    NO_STATUS = "bez statusu"


class EliPublisher(str, Enum):
    """ELI publisher codes for the two official Polish gazette series."""
    DU = "DU"   # Dziennik Ustaw — statutes, regulations, decrees
    MP = "MP"   # Monitor Polski — government announcements, appointments


class VotingResult(str, Enum):
    YES = "YES"
    NO = "NO"
    ABSTAIN = "ABSTAIN"
    ABSENT = "ABSENT"
