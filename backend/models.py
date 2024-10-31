from sqlmodel import Field, SQLModel, create_engine, select, Session, Relationship
from sqlalchemy import Column, DateTime, func, String
from datetime import datetime
from typing import Tuple


class InvestorBase(SQLModel):
    name: str = Field(sa_column=Column("name", String, unique=True))
    investor_type: str
    country: str


class Investor(InvestorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    investment_commitments: list["InvestmentCommitment"] = Relationship(
        back_populates="investor"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> Tuple["Investor", bool]:
        """
        Get an existing investor or create a new one if it doesn't exist.
        Returns tuple of (Investor, created) where created is a boolean
        """
        # Create query based on provided kwargs
        query = select(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.where(getattr(cls, key) == value)

        # Try to get existing investment
        investor = session.exec(query).first()

        if investor is None:
            # Create new investment if it doesn't exist
            investor = cls(**kwargs)
            session.add(investor)
            session.commit()
            session.refresh(investor)
            return investor, True

        return investor, False


class InvestmentCommitment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    investor_id: int | None = Field(default=None, foreign_key="investor.id")
    asset_class: str
    amount: float
    currency: str

    investor: Investor | None = Relationship(back_populates="investment_commitments")

    @classmethod
    def get_or_create(
        cls, session: Session, investor: Investor, **kwargs
    ) -> Tuple["InvestmentCommitment", bool]:
        """
        Get an existing investment commitment or create a new one if it doesn't exist.

        Args:
            session: SQLModel session
            investor: Investor instance
            **kwargs: Other fields for InvestmentCommitment

        Returns:
            Tuple of (InvestmentCommitment, created) where created is a boolean
        """
        # Add investor_id to kwargs
        kwargs["investor_id"] = investor.id

        # Create query based on provided kwargs
        query = select(cls)
        for key, value in kwargs.items():
            if hasattr(cls, key):
                query = query.where(getattr(cls, key) == value)

        # Try to get existing investment commitment
        investment = session.exec(query).first()

        if investment is None:
            # Create new investment commitment if it doesn't exist
            investment = cls(**kwargs)
            investment.investor = investor
            session.add(investment)
            session.commit()
            session.refresh(investment)
            return investment, True

        return investment, False
