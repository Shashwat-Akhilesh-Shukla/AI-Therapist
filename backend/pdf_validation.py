#!/usr/bin/env python3
"""
PDF Upload System Validation Script

Tests the PDF upload and LLM integration fixes.
Run this after deploying the changes.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class PDFUploadValidator:
    def __init__(self, backend_url: str, auth_token: str):
        self.backend_url = backend_url.rstrip('/')
        self.token = auth_token
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        self.results = []

    def log(self, status: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log test result"""
        entry = {
            'status': status,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if details:
            entry['details'] = details
        self.results.append(entry)
        
        icon = '✅' if status == 'PASS' else '❌' if status == 'FAIL' else '⚠️'
        print(f"{icon} [{status}] {message}")
        if details:
            print(f"    Details: {json.dumps(details, indent=2)}")

    def test_pdf_upload_valid(self, pdf_path: str) -> Optional[str]:
        """Test uploading a valid PDF"""
        if not Path(pdf_path).exists():
            self.log('SKIP', f'Test PDF not found: {pdf_path}')
            return None

        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{self.backend_url}/upload_pdf',
                    headers={'Authorization': f'Bearer {self.token}'},
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                doc_id = data.get('doc_id')
                size_kb = data.get('size_kb', 'unknown')
                self.log('PASS', 'Valid PDF upload', {
                    'doc_id': doc_id,
                    'size_kb': size_kb,
                    'status': data.get('status')
                })
                return doc_id
            else:
                self.log('FAIL', 'Valid PDF upload failed', {
                    'status_code': response.status_code,
                    'response': response.text[:200]
                })
                return None
        except Exception as e:
            self.log('FAIL', 'Valid PDF upload exception', {
                'error': str(e)
            })
            return None

    def test_pdf_upload_too_large(self) -> bool:
        """Test that large files are rejected"""
        try:
            # Create a 6MB file
            large_content = b'x' * (6 * 1024 * 1024 + 100)
            files = {'file': ('large.pdf', large_content)}
            
            response = requests.post(
                f'{self.backend_url}/upload_pdf',
                headers={'Authorization': f'Bearer {self.token}'},
                files=files
            )
            
            if response.status_code == 400:
                error_msg = response.json().get('detail', '')
                if 'exceeds' in error_msg.lower():
                    self.log('PASS', 'Large file rejected', {
                        'error': error_msg[:100]
                    })
                    return True
            
            self.log('FAIL', 'Large file should be rejected', {
                'status_code': response.status_code
            })
            return False
        except Exception as e:
            self.log('FAIL', 'Large file test exception', {'error': str(e)})
            return False

    def test_pdf_upload_empty(self) -> bool:
        """Test that empty files are rejected"""
        try:
            files = {'file': ('empty.pdf', b'')}
            
            response = requests.post(
                f'{self.backend_url}/upload_pdf',
                headers={'Authorization': f'Bearer {self.token}'},
                files=files
            )
            
            if response.status_code == 400:
                self.log('PASS', 'Empty file rejected', {
                    'status_code': response.status_code
                })
                return True
            
            self.log('FAIL', 'Empty file should be rejected', {
                'status_code': response.status_code
            })
            return False
        except Exception as e:
            self.log('FAIL', 'Empty file test exception', {'error': str(e)})
            return False

    def test_chat_with_pdf(self, doc_id: str, query: str) -> bool:
        """Test chat with PDF reference"""
        try:
            payload = {
                'message': query,
                'doc_id': doc_id
            }
            
            response = requests.post(
                f'{self.backend_url}/chat',
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                # Check if PDF knowledge was used (heuristic)
                has_reasoning = data.get('reasoning', {})
                pdf_used = has_reasoning.get('pdf_knowledge_used', 0)
                
                self.log('PASS', 'Chat with PDF succeeded', {
                    'pdf_snippets_used': pdf_used,
                    'response_length': len(response_text),
                    'has_response': len(response_text) > 0
                })
                return True
            else:
                self.log('FAIL', 'Chat with PDF failed', {
                    'status_code': response.status_code,
                    'response': response.text[:200]
                })
                return False
        except Exception as e:
            self.log('FAIL', 'Chat with PDF exception', {'error': str(e)})
            return False

    def test_chat_without_doc_id(self, query: str) -> bool:
        """Test that chat works without doc_id"""
        try:
            payload = {'message': query}
            
            response = requests.post(
                f'{self.backend_url}/chat',
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                self.log('PASS', 'Chat without PDF works', {
                    'status_code': response.status_code
                })
                return True
            else:
                self.log('FAIL', 'Chat without PDF failed', {
                    'status_code': response.status_code
                })
                return False
        except Exception as e:
            self.log('FAIL', 'Chat without PDF exception', {'error': str(e)})
            return False

    def test_health_check(self) -> bool:
        """Test that backend is healthy"""
        try:
            response = requests.get(
                f'{self.backend_url}/health',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                self.log('PASS', 'Health check passed', {
                    'status': data.get('status'),
                    'pdf_loader': services.get('pdf_loader', 'unknown')
                })
                return True
            else:
                self.log('FAIL', 'Health check failed', {
                    'status_code': response.status_code
                })
                return False
        except Exception as e:
            self.log('FAIL', 'Health check exception', {'error': str(e)})
            return False

    def run_all_tests(self, pdf_path: Optional[str] = None) -> None:
        """Run all validation tests"""
        print("\n" + "="*60)
        print("PDF Upload System Validation")
        print("="*60 + "\n")

        # Health check
        self.test_health_check()
        
        # Upload tests
        print("\n[Testing Uploads]")
        doc_id = self.test_pdf_upload_valid(pdf_path) if pdf_path else None
        self.test_pdf_upload_too_large()
        self.test_pdf_upload_empty()
        
        # Chat tests
        print("\n[Testing Chat]")
        self.test_chat_without_doc_id("What is your name?")
        
        if doc_id:
            self.test_chat_with_pdf(doc_id, "What is the main topic of the document?")
        else:
            self.log('SKIP', 'Chat with PDF test (no valid PDF uploaded)')
        
        # Summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print test summary"""
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        skipped = sum(1 for r in self.results if r['status'] == 'SKIP')
        
        print("\n" + "="*60)
        print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
        print("="*60)
        
        if failed == 0:
            print("\n✅ All tests passed! PDF upload system is working correctly.")
        else:
            print(f"\n❌ {failed} test(s) failed. Review the logs above.")

def main():
    """Main validation function"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    token = os.getenv('TEST_TOKEN')
    pdf_path = os.getenv('TEST_PDF_PATH')
    
    if not token:
        print("ERROR: TEST_TOKEN environment variable is required")
        print("Usage: TEST_TOKEN=your_token python pdf_validation.py")
        sys.exit(1)
    
    validator = PDFUploadValidator(backend_url, token)
    validator.run_all_tests(pdf_path)

if __name__ == '__main__':
    main()
