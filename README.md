
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
Running Docker
![Running Docker](images/image.png)
uplode textfile
![uplode textfile](images/textfile.png)
scan list
![scan list](images/testfileout.png)
uplode 2 file at a time
![uplode 2 file at a time](images/2textfile.png)
scan list
![scan list](images/2fileout.png)
uplode csv
![uplode csv](images/csv%20file.png)
scan list
![scan list](images/csvfile%20out.png)
latest scan
![latest scan](images/last.png)

## Future Enhancements

If more time and resources were available, the following improvements and features could be implemented:

1. **Database Improvements**  
   - Normalize the database to improve data integrity and reduce redundancy.
   - Optimize queries for better performance with larger datasets.
   - here is the how db looks
   # Normalized Database Design

This document describes the normalized design for the database, which eliminates redundancy and organizes the data into logical groupings.

---

## 1. Main Table: `scans`
Stores general information about each scan.

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `ssn`           | String        | Unique identifier for the record.              |
| `name`          | String        | Name associated with the record.               |
| `upload_date`   | DateTime      | Timestamp of when the record was uploaded.     |

---

## 2. PII Table: `pii`
Stores personally identifiable information (PII) associated with a scan.

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `scan_id`       | Integer       | Foreign key referencing `scans.id`.            |
| `type`          | String        | Type of PII (e.g., `name`, `ssn`, `pan`).      |
| `value`         | String        | The PII value.                                 |

---

## 3. PHI Table: `phi`
Stores protected health information (PHI) associated with a scan.

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `scan_id`       | Integer       | Foreign key referencing `scans.id`.            |
| `type`          | String        | Type of PHI (e.g., `medical_record_number`, `test_results`). |
| `value`         | String        | The PHI value.                                 |

---

## 4. PCI Table: `pci`
Stores payment card information (PCI) associated with a scan.

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `scan_id`       | Integer       | Foreign key referencing `scans.id`.            |
| `value`         | String        | Credit card number or related PCI data.        |

---

## 5. Additional Info Table: `scan_metadata`
Stores metadata about the counts of PII, PHI, and PCI in a scan.

| Column          | Type          | Description                                     |
|------------------|---------------|-------------------------------------------------|
| `id`            | Integer       | Primary key (autoincrement).                   |
| `scan_id`       | Integer       | Foreign key referencing `scans.id`.            |
| `pii_count`     | Integer       | Count of PII items in the scan.                |
| `phi_count`     | Integer       | Count of PHI items in the scan.                |
| `pci_count`     | Integer       | Count of PCI items in the scan.                |

---

## Relationships
- The `scans` table acts as the parent, with one-to-many relationships to the `pii`, `phi`, `pci`, and `scan_metadata` tables.
- Foreign keys (`scan_id`) in the child tables ensure data integrity and establish relationships.

---

## Advantages of Normalization
1. **Eliminates Redundancy:** Data is stored once and referenced as needed, reducing storage requirements.
2. **Improves Data Integrity:** Foreign keys ensure valid relationships between tables.
3. **Facilitates Flexibility:** Adding new data types or columns is simpler without affecting unrelated tables.
4. **Optimizes Queries:** Targeted queries can retrieve specific data without scanning large, monolithic tables.

---

Would you like SQL scripts or an ER diagram to complement this normalized design?


2. **File Type Support**  
   - Extend support to additional file types, such as `.peg` images and advanced PDF structures.

3. **Handling Multiple Records in a Single File**  
   - Develop functionality to parse and handle files containing multiple records efficiently, allowing batch processing.

4. **Enhanced User Experience**  
   - Implement features like file upload progress indicators and detailed logs for user feedback.

5. **Scalability and Deployment**  
   - Transition from SQLite to a more scalable database like PostgreSQL or MySQL for production environments.
   - Add support for horizontal scaling with distributed databases and optimized container configurations.

These enhancements would make the application more robust, scalable, and user-friendly.




