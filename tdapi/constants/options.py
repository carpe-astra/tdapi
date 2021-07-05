"""Option Chains"""

from enum import Enum


class ContractType(str, Enum):
    CALL = "CALL"
    PUT = "PUT"
    ALL = "ALL"


class IncludeQuotes:
    TRUE = True
    FALSE = False


class Strategy(str, Enum):
    SINGLE = "SINGLE"
    ANALYTICAL = "ANALYTICAL"
    COVERED = "COVERED"
    VERTICAL = "VERTICAL"
    CALENDAR = "CALENDAR"
    STRANGLE = "STRANGLE"
    STRADDLE = "STRADDLE"
    BUTTERFLY = "BUTTERFLY"
    CONDOR = "CONDOR"
    DIAGONAL = "DIAGONAL"
    COLLAR = "COLLAR"
    ROLL = "ROLL"


class Range(str, Enum):
    ITM = "ITM"
    NTM = "NTM"
    OTM = "OTM"
    SAK = "SAK"
    SBK = "SBK"
    SNK = "SNK"
    ALL = "ALL"


class Type(str, Enum):
    S = "S"
    NS = "NS"
    ALL = "ALL"


class PutCall(str, Enum):
    PUT = "PUT"
    CALL = "CALL"


class ExchangeName(str, Enum):
    IND = "IND"
    ASE = "ASE"
    NYS = "NYS"
    NAS = "NAS"
    NAP = "NAP"
    PAC = "PAC"
    OPR = "OPR"
    BATS = "BATS"
