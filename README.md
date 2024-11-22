# Aurva
# Aura Project

## Overview
The Aura Project is a web application built using Flask, which processes various document types (images, PDFs, text, and CSV files) to extract sensitive information like PII, PHI, and PCI data. This information is classified and stored in a local SQLite database for further access and management.

## Features
- Upload multiple files at once.
- Extract text from images, PDFs, and CSV files.
- Classify extracted data into PII, PHI, and PCI categories.
- View, search, and delete scan records from the database.

## System Diagram
![System Flowchart](./path_to_your_flowchart_image.png)

## Database Design
The application uses an SQLite database with the following schema:

### `Scan` Table
| Field            | Type    | Description                               |
|------------------|---------|-------------------------------------------|
| `id`             | Integer | Primary key, auto-incremented             |
| `ssn`            | String  | Social Security Number (unique identifier)|
| `name`           | String  | Name of the individual                    |
| `pii`            | String  | Combined PII data                        |
| `phi`            | String  | Combined PHI data                        |
| `pci`            | String  | PCI data                                  |
| `additional_info`| String  | Any unclassified or additional data      |
| `upload_date`    | DateTime| Date and time of upload                   |

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

### Notes
- Ensure that your file uploads are properly configured for the web app.
- The application processes files like `.txt`, `.png`, `.jpg`, `.jpeg`, `.pdf`, and `.csv`.

## License
(Add your license here, if applicable)
