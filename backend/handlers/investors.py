from pydantic import BaseModel
from models import InvestmentCommitment, Investor, InvestorBase
from sqlmodel import Session, select, func
from fastapi import HTTPException


class InvestorOutput(InvestorBase):
    total_commitments: float = 0


class GetInvestorListResponse(BaseModel):
    investors: list[InvestorOutput] = []


class InvestorCreateRequest(BaseModel):
    name: str
    investor_type: str
    country: str


class InvestorGetOrCreateResponse(BaseModel):
    investor: Investor


class InvestorWithCommitments(InvestorBase):
    commitments: list[InvestmentCommitment] | None = None


class InvestmentCommitmentCreateRequest(BaseModel):
    investor_id: int
    asset_class: str
    amount: float
    currency: str


def get_investor_list(session: Session) -> GetInvestorListResponse:
    query = (
        select(
            Investor,
            func.coalesce(func.sum(InvestmentCommitment.amount), 0).label(
                "total_commitments"
            ),
        )
        .join(InvestmentCommitment, isouter=True)
        .group_by(Investor.id)
    )

    results = session.exec(query).all()

    # Convert results to InvestorOutput objects
    investors = []
    for investor, total in results:
        investor_dict = investor.model_dump()
        investor_dict["total_commitments"] = float(total)
        investors.append(InvestorOutput(**investor_dict))

    return GetInvestorListResponse(
        investors=investors,
    )


def create_investor(investor_data: InvestorCreateRequest, session: Session) -> Investor:
    investor, created = Investor.get_or_create(
        session,
        name=investor_data.name,
        investor_type=investor_data.investor_type,
        country=investor_data.country,
    )

    if not created:
        raise HTTPException(
            status_code=400,
            detail=f"Investor with name '{investor_data.name}' already exists",
        )

    return investor


def find_investor(investor_id: int, session: Session) -> InvestorWithCommitments:
    investor = session.get(Investor, investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    statement = select(InvestmentCommitment).where(
        InvestmentCommitment.investor_id == investor_id
    )
    commitments = session.exec(statement)
    result = investor.dict()
    result["commitments"] = commitments
    return result


def create_investment_commitment(
    commitment: InvestmentCommitmentCreateRequest, session: Session
) -> InvestmentCommitment:
    investor = session.get(Investor, commitment.investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")

    investor_commitment, created = InvestmentCommitment.get_or_create(
        session,
        investor=investor,
        asset_class=commitment.asset_class,
        amount=commitment.amount,
        currency=commitment.currency,
    )

    return investor_commitment
