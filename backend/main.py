from models import Investor
from fastapi import FastAPI, Depends, UploadFile, File
from handlers.investors import (
    GetInvestorListResponse,
    InvestorCreateRequest,
    InvestorGetOrCreateResponse,
    InvestorWithCommitments,
    find_investor,
    get_investor_list,
    create_investor,
)
from handlers.upload_csv_data import CSVUploadResponse, upload_csv_handler
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables, engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
async def startup_event():
    create_db_and_tables()


@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    print("Application is shutting down")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post(
    "/upload-csv/",
)
async def upload_csv(session: SessionDep, file: UploadFile) -> CSVUploadResponse:
    response = await upload_csv_handler(file, session)
    return response


@app.get("/investors")
async def get_investors(session: SessionDep) -> GetInvestorListResponse:
    return get_investor_list(session)


@app.post("/investor")
async def post_investor(
    investor_data: InvestorCreateRequest, session: SessionDep
) -> Investor:
    return create_investor(investor_data, session)


@app.get("/investor/{investor_id}")
async def get_investor(investor_id, session: SessionDep) -> InvestorWithCommitments:
    return find_investor(investor_id, session)
