from enum import Enum


class VoteMethodCodesBase(Enum):
    IN_PERSON = "IP"
    MAIL_IN = "MI"
    EARLY_VOTE = "EV"
    PROVISIONAL = "PV"
    ABSENTEE = "AB"


class PoliticalPartyCodesBase(Enum):
    DEMOCRATIC = "DEM"
    REPUBLICAN = "REP"
    LIBERTARIAN = "LIB"
    GREEN = "GRN"
    CONSTITUTION = "CON"
    AMERICAN_SOLIDARITY = "ASP"
    ALLIANCE = "ALL"

    # Additional parties based on various mentions and contexts:
    INDEPENDENT = "IND"
    PROGRESSIVE = "PRO"
    CENTRIST = "CEN"
    MAGA = "MAGA"
    NO_LABELS = "NL"
    LABOUR = "LAB"
    OTHER = "OTH"


class ElectionTypeCodesBase(Enum):
    GENERAL = "GE"
    GENERAL_RUNOFF = "GR"
    GOVERNMENTAL_AUTHORITY = "GA"
    GOVERNMENT_LEGISLATIVE = "GL"
    MUNICIPAL = "ME"
    SPECIAL = "SE"
    RECALL = "RE"
    PRIMARY = "PR"
    PRIMARY_RUNOFF = "PRR"
    OPEN_PRIMARY = "OP"
    CLOSED_PRIMARY = "CP"
    NONPARTISAN_PRIMARY = "NP"
    SCHOOL_BOARD = "SB"
    JUDICIAL = "JE"
    LOCAL = "LE"
    LOCAL_RUNOFF = "LR"
    CONGRESSIONAL = "CE"
    MIDTERM = "ME"
    REFERENDUM = "RF"
    PRESIDENTIAL = "PE"
    PRESIDENTIAL_PRIMARY = "PP"
    PRESIDENTIAL_PREFERENCE = "PPR"
    PRESIDENTIAL_CAUCUS = "PC"
