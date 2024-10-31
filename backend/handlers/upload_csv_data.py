from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
import io
from pydantic import BaseModel
from typing import List
import csv
from models import InvestmentCommitment, Investor


class CSVUploadResponse(BaseModel):
    status: str
    successful_imports: int = 0
    failed_imports: int = 0
    ignored_imports: int = 0
    errors: list[str] = []


async def upload_csv_handler(file: UploadFile, session: Session) -> CSVUploadResponse:
    # Verify file type
    print(file)
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Please upload a CSV file"
        )

    try:
        # Read the contents of the uploaded file
        contents = await file.read()
        # Decode bytes to string and create a StringIO object
        csv_string = io.StringIO(contents.decode("utf-8"))

        # Create CSV reader
        csv_reader = csv.DictReader(csv_string)

        success_count = 0
        error_count = 0
        ignored_import = 0
        errors = []

        # Process each row
        for row_number, row in enumerate(csv_reader, start=1):
            try:
                investor, created = Investor.get_or_create(
                    session,
                    name=row["Investor Name"],
                    investor_type=row["Investory Type"],
                    country=row["Investor Country"],
                    created_at=datetime.strptime(
                        row["Investor Date Added"], "%Y-%m-%d"
                    ),
                    updated_at=datetime.strptime(
                        row["Investor Last Updated"], "%Y-%m-%d"
                    ),
                )

                investment_commitment, created = InvestmentCommitment.get_or_create(
                    session,
                    investor=investor,
                    asset_class=row["Commitment Asset Class"],
                    amount=row["Commitment Amount"],
                    currency=row["Commitment Currency"],
                )

                if created:
                    success_count += 1
                else:
                    ignored_import += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Row {row_number}: {str(e)}")
                session.rollback()

        return {
            "status": "completed",
            "successful_imports": success_count,
            "failed_imports": error_count,
            "ignored_imports": ignored_import,
            "errors": errors,
        }

    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}",
        )
    finally:
        await file.close()
