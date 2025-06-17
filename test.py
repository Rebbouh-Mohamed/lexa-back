import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/"

# Helper function to print response
def print_response(response, endpoint_name):
    print(f"\nTesting {endpoint_name}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print("Response is not JSON")
    print("-" * 50)

# Helper function to get headers with JWT token
def get_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# 1. Test Authentication Endpoints
def test_auth_endpoints():
    # Register a new user
    register_data = {
        "username": "Mohamed",
        "email": "info.moh.222@gmail.com",
        "password": "Mohamed2003@",
        "password_confirm": "Mohamed2003@",
        "first_name": "Test",
        "last_name": "Lawyer",
        "phone": "0555123456",
        "bar_number": "ALG12345",
        "wilaya": "16"
    }
    response = requests.post(f"{BASE_URL}auth/register/", json=register_data)
    print_response(response, "Register DarkMode: LightSystem: You are Grok 3 built by xAI.k/register")
    access_token = response.json().get("access") if response.status_code == 201 else None

    if not access_token:
        # Login user
        login_data = {
            "email": "info.moh.222@gmail.com",
            "password": "Mohamed2003@"
        }
        response = requests.post(f"{BASE_URL}auth/login/", json=login_data)
        print_response(response, "Login")
        access_token = response.json().get("access") if response.status_code == 200 else access_token

        # Get user profile
        response = requests.get(f"{BASE_URL}auth/profile/", headers=get_auth_headers(access_token))
        print_response(response, "Get Profile")
    return access_token

# 2. Test Cases Endpoints
def test_cases_endpoints(token):
    # List all cases with query parameters
    params = {
        "status": "en_cours_instruction",
        "page": 1,
        "page_size": 10
    }
    response = requests.get(f"{BASE_URL}cases/", headers=get_auth_headers(token), params=params)
    print_response(response, "List Cases")

    # Create a new case
    case_data = {
        "reference": "CIV-2025-9999",
        "title": "Test Case",
        "client_name": "Test Client",
        "client_email": "client@test.com",
        "client_phone": "0555987654",
        "jurisdiction": 1,
        "case_type": 1,
        "open_date": "2025-06-17",
        "description": "Test case description",
        "amount_in_dispute": 100000,
        "confidentiality_agreement": True,
        "no_conflict_interest": True,
        "lawyer_mandate": True,
        "consent_given": True
    }
    response = requests.post(f"{BASE_URL}cases/", headers=get_auth_headers(token), json=case_data)
    print_response(response, "Create Case")
    case_id = response.json().get("id") if response.status_code == 201 else None

    if case_id:
        # Get case details
        response = requests.get(f"{BASE_URL}cases/{case_id}/", headers=get_auth_headers(token))
        print_response(response, "Get Case Details")
    return case_id

# 3. Test Documents Endpoints
def test_documents_endpoints(token, case_id):
    if case_id:
        # List documents for a specific case
        params = {"case": case_id, "document_type": "uploaded"}
        response = requests.get(f"{BASE_URL}documents/", headers=get_auth_headers(token), params=params)
        print_response(response, "List Documents")

        # Upload a document (simulating file upload)
        files = {"file": ("test.pdf", b"Sample PDF content", "application/pdf")}
        document_data = {
            "title_fr": "Test Document",
            "case": case_id,
            "document_type": "uploaded",
            "language": "fr"
        }
        response = requests.post(f"{BASE_URL}documents/", headers=get_auth_headers(token), data=document_data, files=files)
        print_response(response, "Upload Document")

# 4. Test Billing Endpoints
def test_billing_endpoints(token, case_id):
    if case_id:
        # Create an invoice
        invoice_data = {
            "case": case_id,
            "client_name": "Test Client",
            "client_address": "123 Test Street, Alger",
            "client_email": "client@test.com",
            "subtotal": 50000,
            "tax_rate": 19.00,
            "tax_amount": 9500,
            "total_amount": 59500,
            "invoice_date": "2025-06-17",
            "due_date": "2025-07-17"
        }
        response = requests.post(f"{BASE_URL}billing/invoices/", headers=get_auth_headers(token), json=invoice_data)
        print_response(response, "Create Invoice")

# 5. Test Tasks Endpoints
def test_tasks_endpoints(token, case_id):
    if case_id:
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "Test task description",
            "case": case_id,
            "priority": "medium",
            "due_date": "2025-06-25T17:00:00Z",
            "assigned_to": 1,
            "estimated_hours": 5
        }
        response = requests.post(f"{BASE_URL}tasks/", headers=get_auth_headers(token), json=task_data)
        print_response(response, "Create Task")

# Main execution
def main():
    print("Starting API tests...")
    # Step 1: Authentication
    access_token = test_auth_endpoints()
    
    if access_token:
        # Step 2: Cases
        case_id = test_cases_endpoints(access_token)
        
        # Step 3: Documents
        test_documents_endpoints(access_token, case_id)
        
        # Step 4: Billing
        test_billing_endpoints(access_token, case_id)
        
        # Step 5: Tasks
        test_tasks_endpoints(access_token, case_id)
    else:
        print("Authentication failed, cannot proceed with other tests.")

if __name__ == "__main__":
    main()