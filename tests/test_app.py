import unittest
from io import BytesIO
from .app import app, db, Scan, classify_data, extract_text_from_image, extract_text_from_pdf
from flask import Flask
from PIL import Image
import pdfplumber
import os

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the Flask test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        self.client = app.test_client()

        # Create the database tables
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_classify_data(self):
        """Test the classify_data function"""
        content = """Name: John Doe
        SSN: 123-45-6789
        PAN: ABCDE1234F
        Credit Card: 1234-5678-9101-1121
        Medical Record Number: 9876543210
        Test Results: Positive"""
        
        pii, phi, pci, additional_info = classify_data(content)

        self.assertIn("name: John Doe", pii)
        self.assertIn("ssn: 123-45-6789", pii)
        self.assertIn("pan: ABCDE1234F", pii)
        self.assertIn("medical_record_number: 9876543210", phi)
        self.assertIn("credit_card: 1234-5678-9101-1121", pci)
        self.assertIn("PII: 3", additional_info)

    def test_extract_text_from_image(self):
        """Test text extraction from an image"""
        # Create a simple image with PIL to test
        image = Image.new('RGB', (100, 100), color='white')
        image_path = '/tmp/test_image.png'
        image.save(image_path)
        with open(image_path, 'rb') as f:
            data = {'file': (BytesIO(f.read()), 'test_image.png')}
            response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)  # Adjust based on expected result
        os.remove(image_path)

    def test_extract_text_from_pdf(self):
        """Test text extraction from a PDF"""
        # Create a simple PDF file to test
        pdf_path = '/tmp/test.pdf'
        with open(pdf_path, 'w') as f:
            f.write('This is a test PDF file.')

        with open(pdf_path, 'rb') as f:
            data = {'file': (BytesIO(f.read()), 'test.pdf')}
            response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)  # Adjust based on expected result
        os.remove(pdf_path)

    def test_home_page(self):
        """Test the home route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload File', response.data)

    def test_scan_listing(self):
        """Test listing of scans"""
        # Add a scan to the database
        new_scan = Scan(ssn='123-45-6789', name='John Doe', pii='name: John Doe', phi='medical_record_number: 9876543210', pci='credit_card: 1234-5678-9101-1121', additional_info='PII: 3, PHI: 1, PCI: 1')
        with app.app_context():
            db.session.add(new_scan)
            db.session.commit()

        response = self.client.get('/scans')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'123-45-6789', response.data)  # Verify the scan is listed

    def test_delete_scan(self):
        """Test deleting a scan"""
        # Add a scan to the database
        new_scan = Scan(ssn='123-45-6789', name='John Doe', pii='name: John Doe', phi='medical_record_number: 9876543210', pci='credit_card: 1234-5678-9101-1121', additional_info='PII: 3, PHI: 1, PCI: 1')
        with app.app_context():
            db.session.add(new_scan)
            db.session.commit()

        response = self.client.post(f'/delete/{new_scan.id}')
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        with app.app_context():
            deleted_scan = Scan.query.get(new_scan.id)
            self.assertIsNone(deleted_scan)  # Ensure the scan is deleted

if __name__ == '__main__':
    unittest.main()
