
# Aura Project

## Overview
This project is a Flask-based web application designed to:
- Upload and process various file formats (`.txt`, `.csv`).
- Extract and classify data into categories such as **PII** (Personally Identifiable Information), **PHI** (Protected Health Information), and **PCI** (Payment Card Information).
- Store the processed data in a database, allowing for record management, search functionality, and retrieval of the latest record.
- Deployed using **Docker** for easy setup and scalability.

## Features

1. **File Upload and Processing**:
   - Supports uploading multiple files at once.
   - Extracts text from images, PDFs, and CSV rows using OCR (`easyocr`) and text-parsing techniques.

2. **Data Classification**:
   - Categorizes extracted information into:
     - **PII**: Name, SSN, PAN.
     - **PHI**: Medical Record Numbers, Test Results.
     - **PCI**: Credit Card Numbers.

3. **Record Management**:
   - Automatically updates records if the same **SSN** is uploaded again, ensuring no duplicate entries.
   - Allows searching for records by **SSN**.
   - Provides functionality to retrieve the latest uploaded record.

4. **View and Delete Records**:
   - View all records stored in the database via a user-friendly web interface.
   - Delete individual records as required.

5. **Dockerized Deployment**:
   - The project is containerized using Docker.
   - Includes a `Dockerfile` and `docker-compose.yml` for easy setup.
   - Orchestrates the Flask application and database.

---

## System Diagram
![System Flowchart](images/system.png)

## Database Design
The database contains a single table called `scan`, with the following structure:

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `ssn`           | String        | Unique identifier for the record.              |
| `name`          | String        | Name associated with the record.               |
| `pii`           | String        | Combined PII information.                      |
| `phi`           | String        | Combined PHI information.                      |
| `pci`           | String        | Combined PCI information.                      |
| `additional_info` | String      | Summary of PII, PHI, and PCI counts.           |
| `upload_date`   | DateTime      | Timestamp of when the record was uploaded.     |

---


## Setup Instructions

### Prerequisites
- Python 3.x
- Pip (Python package manager)
- SQLite (comes pre-installed with Python)

### Steps to Run the Project Locally
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd aura-project
   ```

2. Create a virtual environment and activate it:
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On Mac/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000/` to access the app.

## Docker Setup (Optional)
1. Build the Docker image:
   ```bash
   docker build -t aura-app .
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up
   ```
## Output Snapshot

Here is a snapshot of the application output:

![Running Docker](images/image.png)
![uplode textfile](images/textfile.png)
![scan list](images/testfileout.png)
![uplode 2 file at a time](images/2textfile.png)
![scan list](images/2fileout.png)
![uplode csv](images/csv%20file.png)
![scan list](images/csvfile%20out.png)
![latest scan](images/last.png)



