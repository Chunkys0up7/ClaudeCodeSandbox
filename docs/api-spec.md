# Home Lending Practitioner AI App Store API Specification

## API Overview

This document outlines the REST API endpoints for the Home Lending Practitioner AI App Store.

## Base URL

```
https://api.ai-app-store.homelending.org/v1
```

## Authentication

All API requests require authentication using JWT tokens.

**Headers:**
```
Authorization: Bearer {token}
```

## Endpoints

### Applications

#### List Applications

```
GET /applications
```

**Query Parameters:**
- `limit` (optional): Maximum number of results to return (default: 20)
- `offset` (optional): Offset for pagination (default: 0)
- `category` (optional): Filter by application category
- `status` (optional): Filter by application status

**Response:**
```json
{
  "count": 14,
  "results": [
    {
      "id": "app-123",
      "name": "Loan Eligibility Classifier",
      "description": "AI model to predict loan eligibility",
      "category": "underwriting",
      "status": "active",
      "createdBy": "user-456",
      "createdAt": "2025-01-15T14:32:21Z",
      "updatedAt": "2025-02-10T09:15:43Z"
    },
    ...
  ]
}
```

#### Get Application Details

```
GET /applications/{applicationId}
```

**Response:**
```json
{
  "id": "app-123",
  "name": "Loan Eligibility Classifier",
  "description": "AI model to predict loan eligibility",
  "category": "underwriting",
  "status": "active",
  "createdBy": "user-456",
  "createdAt": "2025-01-15T14:32:21Z",
  "updatedAt": "2025-02-10T09:15:43Z",
  "version": "1.2.0",
  "aiModel": {
    "id": "model-789",
    "type": "classification",
    "framework": "tensorflow",
    "accuracy": 0.92,
    "lastTrainedAt": "2025-01-10T08:45:12Z"
  },
  "permissions": [
    "read:data",
    "write:results",
    "execute:model"
  ],
  "complianceStatus": {
    "fairnessScore": 0.87,
    "biasAuditPassed": true,
    "lastAuditDate": "2025-02-01T00:00:00Z"
  }
}
```

#### Create Application

```
POST /applications
```

**Request Body:**
```json
{
  "name": "Property Valuation Model",
  "description": "AI-powered property value estimation",
  "category": "appraisal",
  "aiModel": {
    "type": "regression",
    "framework": "pytorch"
  }
}
```

**Response:**
```json
{
  "id": "app-456",
  "name": "Property Valuation Model",
  "description": "AI-powered property value estimation",
  "category": "appraisal",
  "status": "draft",
  "createdBy": "user-789",
  "createdAt": "2025-04-11T10:22:33Z",
  "updatedAt": "2025-04-11T10:22:33Z"
}
```

### Users

#### List Users

```
GET /users
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "user-123",
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "role": "admin",
      "createdAt": "2024-12-01T09:30:00Z"
    },
    ...
  ]
}
```

#### Get User Details

```
GET /users/{userId}
```

**Response:**
```json
{
  "id": "user-123",
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role": "admin",
  "createdAt": "2024-12-01T09:30:00Z",
  "applications": [
    {
      "id": "app-456",
      "name": "Property Valuation Model",
      "role": "owner"
    },
    {
      "id": "app-789",
      "name": "Document Classifier",
      "role": "contributor"
    }
  ],
  "lastLogin": "2025-04-10T15:43:22Z"
}
```

### Workflows

#### List Workflows

```
GET /workflows
```

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "workflow-123",
      "name": "Loan Processing Pipeline",
      "description": "End-to-end loan processing workflow",
      "status": "active",
      "createdBy": "user-456",
      "createdAt": "2025-03-01T12:00:00Z"
    },
    ...
  ]
}
```

#### Execute Workflow

```
POST /workflows/{workflowId}/execute
```

**Request Body:**
```json
{
  "inputs": {
    "applicantId": "applicant-123",
    "loanAmount": 250000,
    "propertyId": "property-456"
  },
  "options": {
    "executeAsync": true,
    "notifyComplete": true
  }
}
```

**Response:**
```json
{
  "executionId": "exec-789",
  "status": "initiated",
  "startedAt": "2025-04-11T10:30:45Z",
  "estimatedCompletionTime": "2025-04-11T10:32:00Z"
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error response body:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "The request was invalid",
    "details": "The 'name' field is required"
  }
}
```