import abc
from datetime import datetime, date, timedelta
from typing import Optional

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass as pydantic_dataclass
from sqlmodel import (
    Field as SQLModelField,
    JSON,
    Relationship,
    UniqueConstraint,
    Column,
    DateTime,
    func,
    text,
    SQLModel
)

from sqlalchemy import DateTime, Enum as SA_Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .election_history_codes import (
    ElectionTypeCodesBase,
    VoteMethodCodesBase,
    PoliticalPartyCodesBase
)


class SQLModelBase(SQLModel, abc.ABC):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        arbitrary_types_allowed=True
    )


"""
NOTE: SQLModel will throw an error if relationships are in-tact in the base model without `table=True`.
"""

# Use SQLAlchemy's Enum to create a database column type from the Python Enum
ElectionTypeDB = SA_Enum(ElectionTypeCodesBase, name='election_types', native_enum=False)
VoteMethodDB = SA_Enum(VoteMethodCodesBase, name='vote_methods', native_enum=False)
PolitcalPartyDB = SA_Enum(PoliticalPartyCodesBase, name='political_parties', native_enum=False)


@pydantic_dataclass
class ElectionDataTuple:
    election: "ElectionTypeDetails"
    vote_method: "ElectionVoteMethod"
    vote_record: "ElectionVote"


class ElectionTypeDetailsBase(SQLModelBase):
    id: str = SQLModelField(default_factory=lambda: '', primary_key=True)
    year: int = SQLModelField(...)
    election_type: ElectionTypeCodesBase = SQLModelField(sa_column=ElectionTypeDB)
    state: str = SQLModelField(...)
    city: Optional[str] = SQLModelField(default=None, nullable=True)
    county: Optional[str] = SQLModelField(default=None, nullable=True)
    dates: Optional[list[date]] = SQLModelField(default=None, sa_type=JSON)
    desc: Optional[str] = SQLModelField(default=None, nullable=True)
    created_at: datetime = SQLModelField(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        default=None
    )
    updated_at: datetime = SQLModelField(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        ),
        default=None
    )
    # election_vote_methods: list["ElectionVoteMethodBase"] = None
    # election_voters: list["ElectionVoteBase"] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ElectionTypeDetailsBase):
            return self.id == other.id
        return False

    def generate_hash_key(self) -> str:
        # Create a string with the essential properties of the election
        key_string = f"{self.state}"
        if self.city:
            key_string += f"-{self.city}"
        if self.county:
            key_string += f"-{self.county}"
        key_string += f"-{self.year}-{self.election_type}"
        self.id = key_string.replace(" ", "")
        return self.id

    def add_or_update_vote_method(self, vote_method: "ElectionVoteMethod"):
        for _method in self.election_vote_methods:
            if _method.vote_method == vote_method.vote_method:
                if _method.party == vote_method.party:
                    if _method.vote_date == vote_method.vote_date:
                        return
        self.election_vote_methods.append(vote_method)

    # def update(self, other: 'ElectionTypeDetailsBase'):
    #     if other.city and not self.city:
    #         self.city = other.city
    #     if other.county and not self.county:
    #         self.county = other.county
    #     if other.dates and not self.dates:
    #         self.dates = other.dates
    #     if other.desc and not self.desc:
    #         self.desc = other.desc
    #     for _method in self.election_vote_methods:
    #         for other_method in other.election_vote_methods:
    #             if _method.vote_method == other_method.vote_method:
    #                 _method.vote_method_votes.extend(other_method.vote_method_votes)
    #                 break
    #             else:
    #                 self.election_vote_methods.append(other_method)

    def add_voter_or_update(self, vote_entry: "ElectionVoteBase"):
        for voter in self.election_voters:
            if voter.voter_id == vote_entry.voter_id:
                return
        self.election_voters.append(vote_entry)


class ElectionTypeDetails(ElectionTypeDetailsBase, table=True):
    election_vote_methods: list["ElectionVoteMethod"] = Relationship(
        back_populates="vote_method_election",
        # link_model=ElectionAndVoteMethodLink
    )
    election_voters: list["ElectionVote"] = Relationship(
        back_populates="election"
    )


class ElectionVoteMethodBase(SQLModelBase):
    id: Optional[str] = SQLModelField(default=None, primary_key=True)
    party: Optional[PoliticalPartyCodesBase] = SQLModelField(default=None, sa_column=PolitcalPartyDB)
    vote_date: Optional[date] = SQLModelField(default=None, nullable=True)
    vote_method: VoteMethodCodesBase = SQLModelField(sa_column=VoteMethodDB)
    election_id: str = SQLModelField(foreign_key="electiontypedetails.id", unique=False)
    created_at: Optional[datetime] = SQLModelField(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    updated_at: Optional[datetime] = SQLModelField(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
        default=None
    )
    # vote_method_votes: list["ElectionVoteBase"] = Relationship(back_populates="vote_method")
    # vote_method_election: list["ElectionTypeDetailsBase"] = Relationship(
    #     back_populates="election_vote_methods",
    #     # link_model=ElectionAndVoteMethodLink
    # )

    def __init__(self, **data):
        super().__init__(**data)
        self.id = self.generate_hash_key()

    def __hash__(self):
        return hash(self.id)

    def generate_hash_key(self) -> str:
        key_string: str = f"{self.election_id}"
        if self.vote_method:
            key_string += f"-{self.vote_method}"
        if self.vote_date:
            key_string += f"-{self.vote_date:  %Y%m%d}"
        if self.party:
            key_string += f"-{self.party.value}"

        return key_string


class ElectionVoteMethod(ElectionVoteMethodBase, table=True):
    vote_method_votes: list["ElectionVote"] = Relationship(back_populates="vote_method")
    vote_method_election: list["ElectionTypeDetails"] = Relationship(
        back_populates="election_vote_methods",
        # link_model=ElectionAndVoteMethodLink
    )


class ElectionVoteBase(SQLModelBase):
    __table_args__ = (UniqueConstraint('voter_id', 'election_id', 'vote_method_id'),)
    voter_id: Optional[str] = SQLModelField(foreign_key="recordbasemodel.voter_registration_id", primary_key=True)
    election_id: str = SQLModelField(foreign_key="electiontypedetails.id", primary_key=True)
    vote_method_id: str = SQLModelField(foreign_key="electionvotemethod.id", primary_key=True)
    created_at: Optional[datetime] = SQLModelField(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    updated_at: datetime = SQLModelField(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        ),
        default=None
    )


class ElectionVote(ElectionVoteBase, table=True):
    election: ElectionTypeDetails = Relationship(back_populates="election_voters")
    vote_method: ElectionVoteMethod = Relationship(back_populates="vote_method_votes")
    record: "RecordBaseModel" = Relationship(
        back_populates="vote_history",
    )


class ElectionTurnoutCalculator(SQLModelBase):
    primary_score: float = SQLModelField(default=0.0)
    primary_runoff_score: float = SQLModelField(default=0.0)
    gop_primary_score: float = SQLModelField(default=0.0)
    dem_primary_score: float = SQLModelField(default=0.0)
    gop_primary_runoff_score: float = SQLModelField(default=0.0)
    dem_primary_runoff_score: float = SQLModelField(default=0.0)
    general_score: float = SQLModelField(default=0.0)
    special_score: float = SQLModelField(default=0.0)
    
    def calculate_scores(self, election_list: list[ElectionDataTuple]):
        past_10_years = datetime.now() - timedelta(days=365 * 10)
        
        # Filter out elections that are older than 10 years
        recent_elections = [x for x in election_list if datetime.strptime(x.election.year, '%Y').year > past_10_years.year]
        
        primaries = [x for x in recent_elections if x.election.election_type in ElectionTypeCodesBase.PRIMARY]
        generals = [x for x in recent_elections if x.election.election_type == ElectionTypeCodesBase.GENERAL]
        specials = [x for x in recent_elections if x.election.election_type == ElectionTypeCodesBase.SPECIAL]
        primary_runoffs = [x for x in recent_elections if x.election.election_type == ElectionTypeCodesBase.PRIMARY_RUNOFF]
        
        voted_in_gop_primary = [x for x in primaries if x.vote_method.party == PoliticalPartyCodesBase.REPUBLICAN]
        voted_in_dem_primary = [x for x in primaries if x.vote_method.party == PoliticalPartyCodesBase.DEMOCRATIC]
        voted_in_gop_primary_runoff = [x for x in primary_runoffs if x.vote_method.party == PoliticalPartyCodesBase.REPUBLICAN]
        voted_in_dem_primary_runoff = [x for x in primary_runoffs if x.vote_method.party == PoliticalPartyCodesBase.DEMOCRATIC]
        
        if not recent_elections:
            return self
        self.primary_score = round(len(primaries) / len(recent_elections), 2)
        self.general_score = round(len(generals) / len(recent_elections), 2)
        self.special_score = round(len(specials) / len(recent_elections), 2)
        self.primary_runoff_score = round(len(primary_runoffs) / len(recent_elections), 2)
        self.gop_primary_score = round(len(voted_in_gop_primary) / len(primaries), 2)
        self.dem_primary_score = round(len(voted_in_dem_primary) / len(primaries), 2)
        self.gop_primary_runoff_score = round(len(voted_in_gop_primary_runoff) / len(primary_runoffs), 2)
        self.dem_primary_runoff_score = round(len(voted_in_dem_primary_runoff) / len(primary_runoffs), 2)
        
        return self
        