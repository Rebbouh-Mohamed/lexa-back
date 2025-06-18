  # Legal Case Management System - API Documentation

  ## Base URL
  ```
  http://localhost:8000/api/
  ```

  ## Authentication
  All endpoints require JWT token in header:
  ```
  Authorization: Bearer <access_token>
  ```

  ---

  ## 🔐 Authentication Endpoints

  ### POST `/auth/register/`
  **Register new user**
  ```json
  // Request
  {
    "username": "lawyer123",
    "email": "lawyer@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Ahmed",
    "last_name": "Benali",
    "phone": "0555123456",
    "bar_number": "ALG12345",
    "wilaya": "16"
  }

  // Response
  {
    "user": {
      "id": 1,
      "username": "lawyer123",
      "email": "lawyer@example.com",
      "first_name": "Ahmed",
      "last_name": "Benali",
      "role": "lawyer",
      "status": "pending"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
  ```

  ### POST `/auth/login/`
  **Login user**
  ```json
  // Request
  {
    "email": "lawyer@example.com",
    "password": "password123"
  }

  // Response
  {
    "user": {
      "id": 1,
      "email": "lawyer@example.com",
      "role": "lawyer",
      "status": "active"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
  }
  ```

  ### GET `/auth/profile/`
  **Get user profile**
  ```json
  // Response
  {
    "id": 1,
    "username": "lawyer123",
    "email": "lawyer@example.com",
    "first_name": "Ahmed",
    "last_name": "Benali",
    "role": "lawyer",
    "status": "active",
    "phone": "0555123456",
    "wilaya": "16",
    "profile": {
      "bio": "Experienced lawyer",
      "specializations": ["Civil Law", "Commercial Law"],
      "years_experience": 5
    }
  }
  ```

  ---

  ## ⚖️ Cases Endpoints

  ### GET `/cases/`
  **List all cases**
  ```
  Query Parameters:
  - status: "ouvert", "en_cours_instruction", "juge", "clos"
  - priority: "low", "medium", "high", "urgent"
  - jurisdiction: <jurisdiction_id>
  - case_type: <case_type_id>
  - open_date_after: "2024-01-01"
  - open_date_before: "2024-12-31"
  - search: "search term"
  - page: 1
  - page_size: 20
  ```

  ```json
  // Response
  {
    "count": 45,
    "next": "http://localhost:8000/api/cases/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "reference": "CIV-2025-0001",
        "title": "Affaire Ahmed c/ Société XYZ",
        "client_name": "Ahmed Benali",
        "status": "en_cours_instruction",
        "priority": "medium",
        "open_date": "2025-01-15",
        "close_date": null,
        "jurisdiction_name": "Tribunal de Sidi M'hamed",
        "case_type_name": "Dette commerciale",
        "audiences_count": 2,
        "documents_count": 5
      }
    ]
  }
  ```

  ### POST `/cases/`
  **Create new case**
  ```json
  // Request
  {
    "reference": "CIV-2025-0002",
    "title": "Nouveau litige",
    "client_name": "Fatima Kaci",
    "client_email": "fatima@email.com",
    "client_phone": "0555987654",
    "jurisdiction": 1,
    "case_type": 1,
    "open_date": "2025-06-17",
    "description": "Description du litige",
    "amount_in_dispute": 150000,
    "confidentiality_agreement": true,
    "no_conflict_interest": true,
    "lawyer_mandate": true,
    "consent_given": true
  }

  // Response
  {
    "id": 2,
    "reference": "CIV-2025-0002",
    "title": "Nouveau litige",
    "client_name": "Fatima Kaci",
    "status": "ouvert",
    "created_at": "2025-06-17T10:30:00Z"
  }
  ```

  ### GET `/cases/{id}/`
  **Get case details**
  ```json
  // Response
  {
    "id": 1,
    "reference": "CIV-2025-0001",
    "title": "Affaire Ahmed c/ Société XYZ",
    "client_name": "Ahmed Benali",
    "client_email": "ahmed@email.com",
    "status": "en_cours_instruction",
    "audiences": [
      {
        "id": 1,
        "date": "2025-03-10T09:00:00Z",
        "type_fr": "Mise en état",
        "result_fr": "Report"
      }
    ],
    "metrics": {
      "total_hours_worked": 25.5,
      "total_fees": 125000,
      "documents_count": 5
    }
  }
  ```

  ### GET `/cases/dashboard-stats/`
  **Get dashboard statistics**
  ```json
  // Response
  {
    "total_cases": 45,
    "active_cases": 32,
    "closed_cases": 13,
    "upcoming_audiences": 8,
    "cases_by_status": [
      {"status": "ouvert", "count": 10},
      {"status": "en_cours_instruction", "count": 22}
    ],
    "recent_cases": [...]
  }
  ```

  ---

  ## 📄 Documents Endpoints

  ### GET `/documents/`
  **List documents**
  ```
  Query Parameters:
  - case: <case_id>
  - document_type: "template", "uploaded", "scanned"
  - language: "fr", "ar", "bilingual"
  - is_final: true/false
  - search: "search term"
  ```

  ```json
  // Response
  {
    "count": 25,
    "results": [
      {
        "id": 1,
        "title_fr": "Constitution d'avocat",
        "document_type": "template",
        "language": "fr",
        "case_title": "Affaire Ahmed c/ Société XYZ",
        "case_reference": "CIV-2025-0001",
        "file_name": "constitution.pdf",
        "file_size": 245678,
        "created_at": "2025-01-16T10:00:00Z"
      }
    ]
  }
  ```

  ### POST `/documents/`
  **Upload document**
  ```json
  // Request (multipart/form-data)
  {
    "title_fr": "Nouveau document",
    "case": 1,
    "document_type": "uploaded",
    "language": "fr",
    "file": <file_upload>
  }

  // Response
  {
    "id": 2,
    "title_fr": "Nouveau document",
    "file_name": "document.pdf",
    "file_size": 1024000,
    "created_at": "2025-06-17T10:30:00Z"
  }
  ```

  ### POST `/documents/create-from-template/`
  **Create document from template**
  ```json
  // Request
  {
    "template_id": 1,
    "case_id": 1,
    "title_fr": "Constitution d'avocat - CIV-2025-0001",
    "language": "fr",
    "variables": {
      "jurisdiction": "Tribunal de Sidi M'hamed",
      "client_name": "Ahmed Benali",
      "lawyer_name": "Maître Dupont"
    }
  }

  // Response
  {
    "id": 3,
    "title_fr": "Constitution d'avocat - CIV-2025-0001",
    "content": "Generated document content...",
    "template_name": "Constitution d'Avocat"
  }
  ```

  ---

  ## 💰 Billing Endpoints

  ### GET `/billing/billing/`
  **List billing records**
  ```json
  // Response
  {
    "count": 15,
    "results": [
      {
        "id": 1,
        "invoice_number": "INV-CIV-2025-0001-001",
        "case_title": "Affaire Ahmed c/ Société XYZ",
        "fee_type": "fixed",
        "amount": 50000,
        "total_amount": 62500,
        "payment_status": "paid",
        "invoice_date": "2025-01-20",
        "due_date": "2025-02-20"
      }
    ]
  }
  ```

  ### POST `/billing/invoices/`
  **Create invoice**
  ```json
  // Request
  {
    "case": 1,
    "client_name": "Ahmed Benali",
    "client_address": "123 Rue Example, Alger",
    "client_email": "ahmed@email.com",
    "subtotal": 50000,
    "tax_rate": 19.00,
    "tax_amount": 9500,
    "total_amount": 59500,
    "invoice_date": "2025-06-17",
    "due_date": "2025-07-17"
  }

  // Response
  {
    "id": 2,
    "invoice_number": "INV-CIV-2025-0002-001",
    "status": "draft",
    "total_amount": 59500,
    "outstanding_amount": 59500
  }
  ```

  ### GET `/billing/analytics/revenue/`
  **Revenue analytics**
  ```
  Query Parameters:
  - start_date: "2025-01-01"
  - end_date: "2025-06-17"
  ```

  ```json
  // Response
  {
    "period": {
      "start_date": "2025-01-01",
      "end_date": "2025-06-17"
    },
    "revenue": {
      "total_invoiced": 250000,
      "total_paid": 200000,
      "outstanding": 50000,
      "net_profit": 180000
    },
    "invoices": {
      "total_count": 15,
      "paid_count": 12,
      "overdue_count": 2
    }
  }
  ```

  ---

  ## ✅ Tasks Endpoints

  ### GET `/tasks/`
  **List tasks**
  ```
  Query Parameters:
  - case: <case_id>
  - status: "pending", "in_progress", "completed"
  - priority: "low", "medium", "high", "urgent"
  - assigned_to: <user_id>
  - overdue: true/false
  ```

  ```json
  // Response
  {
    "count": 20,
    "results": [
      {
        "id": 1,
        "title": "Préparer dossier client",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2025-06-20T17:00:00Z",
        "case_title": "Affaire Ahmed c/ Société XYZ",
        "assigned_to_name": "Ahmed Benali",
        "progress_percentage": 75,
        "is_overdue": false
      }
    ]
  }
  ```

  ### POST `/tasks/`
  **Create task**
  ```json
  // Request
  {
    "title": "Nouvelle tâche",
    "description": "Description de la tâche",
    "case": 1,
    "priority": "medium",
    "due_date": "2025-06-25T17:00:00Z",
    "assigned_to": 1,
    "estimated_hours": 5
  }

  // Response
  {
    "id": 2,
    "title": "Nouvelle tâche",
    "status": "pending",
    "created_at": "2025-06-17T10:30:00Z"
  }
  ```

  ### GET `/tasks/dashboard/`
  **Task dashboard stats**
  ```json
  // Response
  {
    "total_tasks": 20,
    "pending_tasks": 8,
    "in_progress_tasks": 5,
    "completed_tasks": 7,
    "overdue_tasks": 2,
    "due_today": 3,
    "due_this_week": 8
  }
  ```

  ---

  ## 🔔 Notifications Endpoints

  ### GET `/notifications/`
  **List notifications**
  ```
  Query Parameters:
  - notification_type: "task_due", "audience_reminder", "case_update"
  - is_read: true/false
  - priority: "low", "medium", "high"
  ```

  ```json
  // Response
  {
    "count": 12,
    "results": [
      {
        "id": 1,
        "title": "Tâche due demain",
        "message": "Votre tâche 'Préparer dossier' est due demain",
        "notification_type": "task_due",
        "priority": "high",
        "is_read": false,
        "created_at": "2025-06-17T09:00:00Z"
      }
    ]
  }
  ```

  ### POST `/notifications/{id}/mark-read/`
  **Mark notification as read**
  ```json
  // Response
  {
    "message": "Notification marked as read"
  }
  ```

  ### GET `/notifications/count/`
  **Get unread count**
  ```json
  // Response
  {
    "unread_count": 5
  }
  ```

  ---

  ## 🏛️ Legal Framework Endpoints

  ### GET `/legal-framework/courts/`
  **List Algerian courts**
  ```
  Query Parameters:
  - court_level: "premiere", "appel", "cassation"
  - jurisdiction_type: "civil", "penal", "commercial"
  - wilaya: "16", "31", etc.
  ```

  ```json
  // Response
  {
    "count": 50,
    "results": [
      {
        "id": 1,
        "court_name_fr": "Tribunal de Sidi M'hamed",
        "court_name_ar": "محكمة سيدي امحمد",
        "court_level": "premiere",
        "jurisdiction_type": "civil",
        "wilaya": "16",
        "city": "Alger",
        "president": "Ahmed Benamar"
      }
    ]
  }
  ```

  ### GET `/legal-framework/legal-codes/`
  **List legal codes**
  ```
  Query Parameters:
  - code_type: "civil", "penal", "commerce"
  ```

  ```json
  // Response
  {
    "count": 100,
    "results": [
      {
        "id": 1,
        "code_name_fr": "Code Civil Algérien",
        "code_type": "civil",
        "article_number": "124",
        "article_title_fr": "Obligation de payer les dettes",
        "article_content_fr": "Tout débiteur doit s'acquitter..."
      }
    ]
  }
  ```

  ### GET `/legal-framework/tax-rate/{tax_type}/`
  **Get current tax rate**
  ```json
  // Response for /legal-framework/tax-rate/tva/
  {
    "tax_type": "tva",
    "tax_rate": 19.00,
    "description_fr": "Taxe sur la Valeur Ajoutée",
    "effective_from": "2017-01-01",
    "is_active": true
  }
  ```

  ---

  ## 👥 Client Portal Endpoints

  ### POST `/client-portal/generate-access/`
  **Generate client access**
  ```json
  // Request
  {
    "case_id": 1,
    "client_email": "client@email.com",
    "expires_days": 30
  }

  // Response
  {
    "id": 1,
    "access_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "client_email": "client@email.com",
    "expires_at": "2025-07-17T10:30:00Z",
    "case_title": "Affaire Ahmed c/ Société XYZ"
  }
  ```

  ### POST `/client-portal/verify-access/`
  **Verify client access (Public)**
  ```json
  // Request
  {
    "access_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "client_email": "client@email.com"
  }

  // Response
  {
    "valid": true,
    "case": {
      "case_reference": "CIV-2025-0001",
      "case_title": "Affaire Ahmed c/ Société XYZ",
      "status": "en_cours_instruction",
      "description": "Description du litige",
      "open_date": "2025-01-15"
    },
    "access_expires": "2025-07-17T10:30:00Z"
  }
  ```

  ### POST `/client-portal/send-message/`
  **Send client message (Public)**
  ```json
  // Request
  {
    "access_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "client_email": "client@email.com",
    "sender_name": "Ahmed Benali",
    "subject": "Question sur le dossier",
    "message": "Bonjour, j'aimerais savoir..."
  }

  // Response
  {
    "id": 1,
    "subject": "Question sur le dossier",
    "message": "Bonjour, j'aimerais savoir...",
    "sender_type": "client",
    "created_at": "2025-06-17T10:30:00Z"
  }
  ```

  ---

  ## 👨‍💼 Admin Panel Endpoints

  ### GET `/admin-panel/users/`
  **List all users (Admin only)**
  ```
  Query Parameters:
  - role: "lawyer", "admin", "assistant"
  - status: "active", "pending", "blocked"
  - wilaya: "16", "31", etc.
  ```

  ```json
  // Response
  {
    "count": 100,
    "results": [
      {
        "id": 1,
        "email": "lawyer@example.com",
        "full_name": "Ahmed Benali",
        "role": "lawyer",
        "status": "active",
        "subscription_status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "last_sign_in_at": "2025-06-17T09:30:00Z"
      }
    ]
  }
  ```

  ### POST `/admin-panel/users/{id}/approve/`
  **Approve user (Admin only)**
  ```json
  // Request
  {
    "reason": "User documents verified"
  }

  // Response
  {
    "message": "User approved successfully"
  }
  ```

  ### GET `/admin-panel/dashboard/`
  **Admin dashboard stats**
  ```json
  // Response
  {
    "users": {
      "total": 100,
      "active": 85,
      "pending": 10,
      "blocked": 5,
      "new_this_month": 15
    },
    "subscriptions": {
      "total": 85,
      "active": 70,
      "trial": 10,
      "expired": 5,
      "revenue_this_month": 1500000
    }
  }
  ```

  ---

  ## 📊 Analytics Endpoints

  ### GET `/analytics/case-performance/`
  **Case performance analytics**
  ```
  Query Parameters:
  - start_date: "2025-01-01"
  - end_date: "2025-06-17"
  ```

  ```json
  // Response
  {
    "period": {
      "start_date": "2025-01-01",
      "end_date": "2025-06-17"
    },
    "case_metrics": {
      "total_cases": 45,
      "completed_cases": 13,
      "active_cases": 32,
      "average_duration_days": 145.5
    },
    "financial_metrics": {
      "total_revenue": 2500000,
      "paid_revenue": 2000000,
      "net_profit": 1800000,
      "average_case_value": 192307
    },
    "monthly_trends": [
      {
        "month": "2025-01",
        "revenue": 450000,
        "cases_opened": 8
      }
    ]
  }
  ```

  ---

  ## ⚙️ Common Response Formats

  ### Success Response
  ```json
  {
    "data": {...},
    "message": "Operation successful"
  }
  ```

  ### Error Response
  ```json
  {
    "error": "Error message",
    "details": {
      "field_name": ["Field error message"]
    }
  }
  ```

  ### Pagination Response
  ```json
  {
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=2",
    "previous": null,
    "results": [...]
  }
  ```

  ---

  ## 📝 Common Query Parameters
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 20, max: 100)
  - `search`: Search term for text fields
  - `ordering`: Sort by field (prefix with `-` for descending)

  ## 🔒 Permission Levels
  - **Public**: No authentication required
  - **Authenticated**: Valid JWT token required
  - **Lawyer**: User role must be 'lawyer' or 'admin'
  - **Admin**: User role must be 'admin'

  ## 📋 Status Codes
  - `200`: Success
  - `201`: Created
  - `400`: Bad Request
  - `401`: Unauthorized
  - `403`: Forbidden
  - `404`: Not Found
  - `500`: Server Error