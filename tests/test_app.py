import os
import pytest
from io import BytesIO
from app import app, db, Scan
import random
import string

TEST_DB_PATH = "test_database.db"

# Ensure the test database file is removed before running tests
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)


@pytest.fixture(scope="module")
def test_client():
    # Set up the application for testing
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{TEST_DB_PATH}"  # Use a test-specific database
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()  # Create the tables for the test
    yield app.test_client()  # Yield the test client for use in the test functions
    with app.app_context():
        db.drop_all()  # Drop all tables after the tests are finished


# Helper function to generate unique SSN for each test
def generate_unique_ssn():
    return "".join(random.choices(string.digits, k=11))


# Test home route
def test_home(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert (
        b"Upload File" in response.data
    )  # Check if the word 'Upload File' is present in the home page


# Test upload file route with valid file (e.g., .txt file)
def test_upload_text_file(test_client):
    data = {"file": (BytesIO(b"NAME: John Doe\nSSN: 123-45-6789\n"), "test.txt")}
    response = test_client.post(
        "/upload", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 302  # Check if the redirect happened
    assert (
        "/scans" in response.headers["Location"]
    )  # Check that the redirect is to the scans list


# Test upload file route with missing file
def test_upload_missing_file(test_client):
    response = test_client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"No file provided!" in response.data  # Check for the error message


# Test scanning route
def test_list_scans(test_client):
    with app.app_context():
        # Ensure database operations are inside the app context
        # Add a scan to the database with a unique SSN
        scan = Scan(
            ssn=generate_unique_ssn(),
            name="John Doe",
            pii="name: John Doe, ssn: 123-45-6789",
            phi="medical_record_number: 12345",
            pci="credit_card: 1234-5678-9876-5432",
            additional_info="PII: 1, PHI: 1, PCI: 1",
        )
        db.session.add(scan)
        db.session.commit()

    # Test if the scan appears in the scans list page
    response = test_client.get("/scans")
    assert response.status_code == 200
    assert b"John Doe" in response.data  # Check if the scan's name appears in the list


# Test search route with invalid SSN
def test_search_scan_invalid(test_client):
    # Test searching for a non-existing scan
    response = test_client.get("/search?ssn=000000000")
    assert response.status_code == 200
    assert (
        b"No scan found for the given SSN" in response.data
    )  # Check if the message appears for no result


# Test delete scan functionality


# Test getting the last scan
def test_last_scan(test_client):
    with app.app_context():
        # Add a scan to the database with a unique SSN
        scan = Scan(
            ssn=generate_unique_ssn(),
            name="Alice Doe",
            pii="name: Alice Doe",
            phi="medical_record_number: 11111",
            pci="credit_card: 1111-2222-3333-4444",
            additional_info="PII: 1, PHI: 1, PCI: 1",
        )
        db.session.add(scan)
        db.session.commit()

    # Test getting the last scan
    response = test_client.get("/last_scan")
    assert response.status_code == 200
    assert (
        b"Alice Doe" in response.data
    )  # Check if the name appears in the last scan response


# Clean up the database after all tests
@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    # Remove the test database file after the tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
