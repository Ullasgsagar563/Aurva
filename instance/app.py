from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import easyocr
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import pdfplumber
import logging

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
app.logger = logging.getLogger(__name__)

# Database model
class Scan(db.Model):
    __tablename__ = 'scan'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ssn = db.Column(db.String, unique=True, nullable=False)  # Primary identifier
    name = db.Column(db.String, nullable=True)
    pii = db.Column(db.String, nullable=True)  # All PII info combined
    phi = db.Column(db.String, nullable=True)  # All PHI info combined
    pci = db.Column(db.String, nullable=True)  # All PCI info combined
    additional_info = db.Column(db.String, nullable=True)  # Unclassified info or extra details
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

# Utility function for classification
def classify_data(file_content):
    patterns = {
        'name': r'(?i)\bname:\s*([A-Za-z\s]+)(?=\n|$)',
        'pan': r'(?i)\bpan:\s*([A-Z]{5}[0-9]{4}[A-Z])',
        'ssn': r'(?i)\bssn:\s*([0-9]{3}-[0-9]{2}-[0-9]{4})',
        'credit_card': r'(?i)\bcredit\s*card:\s*([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4})',
        'medical_record_number': r'(?i)\bmedical\s*record\s*number:\s*([0-9]+)',
        'test_results': r'(?i)\btest\s*results:\s*(.*?)(?:\n|$)'
    }

    classified_data = {}
    counts = {'PII': 0, 'PHI': 0, 'PCI': 0}
    unclassified = []

    # Extract the data
    for key, pattern in patterns.items():
        match = re.search(pattern, file_content)
        if match:
            classified_data[key] = match.group(1)
            if key in ['name', 'pan', 'ssn']:
                counts['PII'] += 1
            elif key in ['medical_record_number', 'test_results']:
                counts['PHI'] += 1
            elif key == 'credit_card':
                counts['PCI'] += 1
        else:
            classified_data[key] = None

    # Combine classified information
    pii = f"name: {classified_data.get('name')}, ssn: {classified_data.get('ssn')}, pan: {classified_data.get('pan')}"
    phi = f"medical_record_number: {classified_data.get('medical_record_number')}, test_results: {classified_data.get('test_results')}"
    pci = f"credit_card: {classified_data.get('credit_card')}"
    additional_info = f"PII: {counts['PII']}, PHI: {counts['PHI']}, PCI: {counts['PCI']}"

    return pii, phi, pci, additional_info

# Text extraction functions
def extract_text_from_image(file):
    image = Image.open(file.stream)
    image_np = np.array(image)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_np, detail=0)
    return "\n".join(text)

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df  # Return the entire dataframe for row-by-row processing

# Routes
@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file provided!", 400

    files = request.files.getlist('file')  # Retrieve the list of uploaded files
    if not files:
        return "No files selected!", 400

    for file in files:
        app.logger.info(f"Processing file: {file.filename}")
        print("Processing file:", file.filename)
        content = ""
        
        if file.filename.endswith('.txt'):
            content = file.read().decode('utf-8')
        elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
            content = extract_text_from_image(file)
        elif file.filename.endswith('.pdf'):
            content = extract_text_from_pdf(file)
        elif file.filename.endswith('.csv'):
            df = extract_text_from_csv(file)
            for index, row in df.iterrows():
                content = "\n".join([f"{col}: {row[col]}" for col in df.columns])
                app.logger.info(f"Extracted content for row {index}: {content}")
                print(f"Extracted content for row {index}:", content)
                pii, phi, pci, additional_info = classify_data(content)

                ssn = row.get('SSN', None)
                if not ssn:
                    app.logger.warning(f"Missing SSN in file: {file.filename}")
                    print(f"No valid SSN found in row {index}; skipping row.")
                    continue

                ssn = re.sub(r'\D', '', ssn)  # Normalize SSN
                name = row.get('Name', None)

                scan = Scan.query.filter_by(ssn=ssn).first()

                if scan:
                    scan.name = name
                    scan.pii = pii
                    scan.phi = phi
                    scan.pci = pci
                    scan.additional_info = additional_info
                    scan.upload_date = datetime.utcnow()
                else:
                    scan = Scan(
                        ssn=ssn,
                        name=name,
                        pii=pii,
                        phi=phi,
                        pci=pci,
                        additional_info=additional_info
                    )
                    db.session.add(scan)
        else:
            continue

        # Process .txt files separately
        if file.filename.endswith('.txt'):
            pii, phi, pci, additional_info = classify_data(content)

            ssn_match = re.search(r'SSN[:\s]*([\d-]+)', content)
            ssn = ssn_match.group(1) if ssn_match else None
            ssn = re.sub(r'\D', '', ssn)  # Normalize SSN

            name_match = re.search(r'NAME[:\s]*([A-Za-z\s]+)(?=\n|$)', content)
            name = name_match.group(1) if name_match else None

            if not ssn:
                print(f"No valid SSN found; skipping file.")
                continue  # Skip file if no SSN found

            scan = Scan.query.filter_by(ssn=ssn).first()

            if scan:
                scan.name = name
                scan.pii = pii
                scan.phi = phi
                scan.pci = pci
                scan.additional_info = additional_info
                scan.upload_date = datetime.utcnow()
            else:
                scan = Scan(
                    ssn=ssn,
                    name=name,
                    pii=pii,
                    phi=phi,
                    pci=pci,
                    additional_info=additional_info
                )
                db.session.add(scan)

    db.session.commit()
    return redirect(url_for('list_scans'))

@app.route('/scans', methods=['GET'])
def list_scans():
    scans = Scan.query.all()
    return render_template('list.html', scans=scans)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_scan(id):
    scan = Scan.query.get(id)
    if not scan:
        return "Scan not found!", 404

    db.session.delete(scan)
    db.session.commit()
    return redirect(url_for('list_scans'))
    
@app.route('/last_scan', methods=['GET'])
def get_last_scan():
    last_scan = Scan.query.order_by(Scan.upload_date.desc()).first()  # Get the most recent scan
    if last_scan:
        # Return the scan information as JSON
        return {
            'ssn': last_scan.ssn,
            'name': last_scan.name,
            'pii': last_scan.pii,
            'phi': last_scan.phi,
            'pci': last_scan.pci,
            'additional_info': last_scan.additional_info,
            'upload_date': last_scan.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        return {'message': 'No scan found'}


@app.route('/search', methods=['GET'])
def search_scan():
    ssn = request.args.get('ssn')  # Get the SSN from the query string
    
    if not ssn:
        return redirect(url_for('list_scans'))  # Redirect if SSN is not provided

    ssn = re.sub(r'\D', '', ssn)  # Normalize SSN format

    print(f"Searching for SSN: {ssn}")

    scan = Scan.query.filter_by(ssn=ssn).first()

    if scan:
        print(f"Found scan for SSN {ssn}: {scan.name}")
        return render_template('search_result.html', scan=scan)
    else:
        print(f"No scan found for SSN {ssn}")
        return render_template('search_result.html', message="No scan found for the given SSN")


# Initialize database
with app.app_context():
    db.drop_all()
    db.create_all()

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
