import pytest
from fastapi.testclient import TestClient
from main import app, get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import os


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///test.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def cleanup_db():
    """Create a fresh database for each test"""
    # Remove test database if it exists
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def sample_csv():
    # Create a temporary CSV file for testing
    csv_content = """Investor Name,Investory Type,Investor Country,Investor Date Added,Investor Last Updated,Commitment Asset Class,Commitment Amount,Commitment Currency
Ioo Gryffindor fund,fund manager,Singapore,2000-07-06,2024-02-21,Infrastructure,15000000,GBP
Ibx Skywalker ltd,asset manager,United States,1997-07-21,2024-02-21,Infrastructure,31000000,GBP
Cza Weasley fund,wealth manager,United Kingdom,2002-05-29,2024-02-21,Hedge Funds,58000000,GBP
Mjd Jedi fund,bank,China,2010-06-08,2024-02-21,Private Equity,72000000,GBP
Mjd Jedi fund,bank,China,2010-06-08,2024-02-21,Natural Resources,1000000,GBP"""

    file_path = "test_sample.csv"
    with open(file_path, "w") as f:
        f.write(csv_content)

    yield file_path

    # Cleanup after test
    if os.path.exists(file_path):
        os.remove(file_path)


def test_create_and_get_investor(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    json_dict = {
        "name": "ahmad faiyaz",
        "investor_type": "hedge fund",
        "country": "Bangladesh",
    }

    # Test valid path
    response = client.post(
        "/investor",
        json=json_dict,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "ahmad faiyaz"

    # Should throw error if we try to create again
    response = client.post(
        "/investor",
        json=json_dict,
    )

    assert response.status_code == 400

    # Should return above json
    response = client.get(
        "/investor/1",
    )

    json_dict["commitments"] = []

    assert response.status_code == 200
    assert response.json() == json_dict

    commitment_data = {
        "investor_id": 1,
        "asset_class": "real-estate",
        "amount": 5000,
        "currency": "GBP",
    }

    response = client.post(
        "/investment-commitment",
        json=commitment_data,
    )

    expected_response = {
        "id": 1,
        "amount": 5000.0,
        "investor_id": 1,
        "asset_class": "real-estate",
        "currency": "GBP",
    }

    assert response.status_code == 200
    assert response.json() == expected_response

    response = client.get(
        "/investor/1",
    )
    json_dict["commitments"].append(expected_response)

    assert response.status_code == 200
    assert response.json() == json_dict

    # Should be 404
    response = client.get(
        "/investor/2",
    )

    assert response.status_code == 404

    # should list all the investors
    response = client.get(
        "/investors",
    )
    expected_data = {
        "investors": [
            {
                "name": "ahmad faiyaz",
                "investor_type": "hedge fund",
                "country": "Bangladesh",
                "total_commitments": 5000.0,
            }
        ]
    }
    assert response.json() == expected_data

    # Clean up dependency override
    app.dependency_overrides.clear()


def test_csv_upload_validate_data(session: Session, sample_csv):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    with open(sample_csv, "rb") as f:
        files = {"file": ("test.csv", f, "text/csv")}
        response = client.post("/upload-csv/", files=files)

        expected_response = {
            "status": "completed",
            "successful_imports": 5,
            "failed_imports": 0,
            "ignored_imports": 0,
            "errors": [],
        }

        assert response.json() == expected_response

        response = client.get(
            "/investors",
        )

        expected_response = {
            "investors": [
                {
                    "name": "Ioo Gryffindor fund",
                    "investor_type": "fund manager",
                    "country": "Singapore",
                    "total_commitments": 15000000.0,
                },
                {
                    "name": "Ibx Skywalker ltd",
                    "investor_type": "asset manager",
                    "country": "United States",
                    "total_commitments": 31000000.0,
                },
                {
                    "name": "Cza Weasley fund",
                    "investor_type": "wealth manager",
                    "country": "United Kingdom",
                    "total_commitments": 58000000.0,
                },
                {
                    "name": "Mjd Jedi fund",
                    "investor_type": "bank",
                    "country": "China",
                    "total_commitments": 73000000.0,
                },
            ]
        }

        assert response.json() == expected_response

        response = client.get(
            "/investor/4",
        )

        expected_response = {
            "name": "Mjd Jedi fund",
            "investor_type": "bank",
            "country": "China",
            "commitments": [
                {
                    "id": 4,
                    "amount": 72000000.0,
                    "investor_id": 4,
                    "asset_class": "Private Equity",
                    "currency": "GBP",
                },
                {
                    "id": 5,
                    "amount": 1000000.0,
                    "investor_id": 4,
                    "asset_class": "Natural Resources",
                    "currency": "GBP",
                },
            ],
        }

        assert response.json() == expected_response
