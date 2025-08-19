# 🧳 Stasher Customer API Documentation

## Overview

This document provides comprehensive API documentation for customer-related endpoints in the Stasher bag storage service. The API allows customers to manage their profiles and bookings for storing bags at various stashpoints.

## Base URL
```
http://localhost:5001/api/v1
```

## Authentication
*Note: The current implementation doesn't include authentication, but in a production environment, these endpoints would require proper authentication and authorization.*

---

## 📋 Customer Endpoints

### 1. Create Customer
Creates a new customer account.

**Endpoint:** `POST /customers`

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890"
}
```

**Request Schema:**
- `name` (string, required): Customer's full name (max 255 characters)
- `email` (string, required): Customer's email address (max 255 characters, must be unique)
- `phone` (string, optional): Customer's phone number (max 20 characters)

**Success Response:** `201 Created`
```json
{
  "id": "a1b2c3d4e5f6",
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data or missing required fields
- `409 Conflict`: Email already exists

---

### 2. Get Customer
Retrieves customer information by ID.

**Endpoint:** `GET /customers/{customer_id}`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier

**Success Response:** `200 OK`
```json
{
  "id": "a1b2c3d4e5f6",
  "name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+1234567890",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Error Responses:**
- `404 Not Found`: Customer not found

---

### 3. Update Customer
Updates customer information.

**Endpoint:** `PUT /customers/{customer_id}`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier

**Request Body:**
```json
{
  "name": "John Smith Updated",
  "email": "john.updated@example.com",
  "phone": "+1987654321"
}
```

**Success Response:** `200 OK`
```json
{
  "id": "a1b2c3d4e5f6",
  "name": "John Smith Updated",
  "email": "john.updated@example.com",
  "phone": "+1987654321",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Customer not found
- `409 Conflict`: Email already exists (if email is being changed)

---

### 4. Delete Customer
Deletes a customer account.

**Endpoint:** `DELETE /customers/{customer_id}`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier

**Success Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Customer not found
- `409 Conflict`: Customer has active bookings

---

## 📋 Customer Booking Endpoints

### 5. Get Customer Bookings
Retrieves all bookings for a specific customer.

**Endpoint:** `GET /customers/{customer_id}/bookings`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier

**Query Parameters:**
- `status` (string, optional): Filter by booking status (`active`, `completed`, `cancelled`)
- `limit` (integer, optional): Maximum number of results (default: 50)
- `offset` (integer, optional): Number of results to skip (default: 0)

**Success Response:** `200 OK`
```json
{
  "bookings": [
    {
      "id": "booking123",
      "created_at": "2024-01-15T09:00:00.000000",
      "bag_count": 2,
      "dropoff_time": "2024-01-20T10:00:00.000000",
      "pickup_time": "2024-01-20T18:00:00.000000",
      "is_paid": true,
      "is_cancelled": false,
      "checked_in": true,
      "checked_out": false,
      "stashpoint_id": "stash456",
      "customer_id": "a1b2c3d4e5f6",
      "stashpoint": {
        "id": "stash456",
        "name": "Central Cafe Storage",
        "address": "123 Main Street",
        "latitude": 51.5107,
        "longitude": -0.1246
      }
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Error Responses:**
- `404 Not Found`: Customer not found

---

### 6. Create Booking
Creates a new booking for a customer.

**Endpoint:** `POST /customers/{customer_id}/bookings`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier

**Request Body:**
```json
{
  "stashpoint_id": "stash456",
  "bag_count": 2,
  "dropoff_time": "2024-01-20T10:00:00Z",
  "pickup_time": "2024-01-20T18:00:00Z"
}
```

**Request Schema:**
- `stashpoint_id` (string, required): ID of the stashpoint to book
- `bag_count` (integer, required): Number of bags to store (minimum: 1)
- `dropoff_time` (string, required): ISO datetime when bags will be dropped off
- `pickup_time` (string, required): ISO datetime when bags will be picked up

**Success Response:** `201 Created`
```json
{
  "id": "booking789",
  "created_at": "2024-01-15T09:00:00.000000",
  "bag_count": 2,
  "dropoff_time": "2024-01-20T10:00:00.000000",
  "pickup_time": "2024-01-20T18:00:00.000000",
  "is_paid": false,
  "is_cancelled": false,
  "checked_in": false,
  "checked_out": false,
  "stashpoint_id": "stash456",
  "customer_id": "a1b2c3d4e5f6"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data or booking conflicts
- `404 Not Found`: Customer or stashpoint not found
- `409 Conflict`: Stashpoint not available for the requested time/capacity

---

### 7. Get Booking Details
Retrieves detailed information about a specific booking.

**Endpoint:** `GET /customers/{customer_id}/bookings/{booking_id}`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier
- `booking_id` (string): Unique booking identifier

**Success Response:** `200 OK`
```json
{
  "id": "booking789",
  "created_at": "2024-01-15T09:00:00.000000",
  "bag_count": 2,
  "dropoff_time": "2024-01-20T10:00:00.000000",
  "pickup_time": "2024-01-20T18:00:00.000000",
  "is_paid": false,
  "is_cancelled": false,
  "checked_in": false,
  "checked_out": false,
  "stashpoint_id": "stash456",
  "customer_id": "a1b2c3d4e5f6",
  "stashpoint": {
    "id": "stash456",
    "name": "Central Cafe Storage",
    "address": "123 Main Street",
    "latitude": 51.5107,
    "longitude": -0.1246,
    "capacity": 20,
    "open_from": "08:00",
    "open_until": "22:00"
  }
}
```

**Error Responses:**
- `404 Not Found`: Customer or booking not found
- `403 Forbidden`: Booking doesn't belong to the customer

---

### 8. Update Booking
Updates booking details (limited fields can be updated).

**Endpoint:** `PUT /customers/{customer_id}/bookings/{booking_id}`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier
- `booking_id` (string): Unique booking identifier

**Request Body:**
```json
{
  "bag_count": 3,
  "dropoff_time": "2024-01-20T11:00:00Z",
  "pickup_time": "2024-01-20T19:00:00Z"
}
```

**Note:** Only unpaid and non-checked-in bookings can be updated.

**Success Response:** `200 OK`
```json
{
  "id": "booking789",
  "created_at": "2024-01-15T09:00:00.000000",
  "bag_count": 3,
  "dropoff_time": "2024-01-20T11:00:00.000000",
  "pickup_time": "2024-01-20T19:00:00.000000",
  "is_paid": false,
  "is_cancelled": false,
  "checked_in": false,
  "checked_out": false,
  "stashpoint_id": "stash456",
  "customer_id": "a1b2c3d4e5f6"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input data or booking cannot be updated
- `404 Not Found`: Customer or booking not found
- `403 Forbidden`: Booking doesn't belong to the customer

---

### 9. Cancel Booking
Cancels a booking.

**Endpoint:** `POST /customers/{customer_id}/bookings/{booking_id}/cancel`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier
- `booking_id` (string): Unique booking identifier

**Success Response:** `200 OK`
```json
{
  "id": "booking789",
  "is_cancelled": true,
  "message": "Booking cancelled successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Booking cannot be cancelled (already checked in)
- `404 Not Found`: Customer or booking not found
- `403 Forbidden`: Booking doesn't belong to the customer

---

### 10. Check-in Booking
Marks a booking as checked in (bags dropped off).

**Endpoint:** `POST /customers/{customer_id}/bookings/{booking_id}/checkin`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier
- `booking_id` (string): Unique booking identifier

**Success Response:** `200 OK`
```json
{
  "id": "booking789",
  "checked_in": true,
  "message": "Bags checked in successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Booking not paid or already checked in
- `404 Not Found`: Customer or booking not found
- `403 Forbidden`: Booking doesn't belong to the customer

---

### 11. Check-out Booking
Marks a booking as checked out (bags picked up).

**Endpoint:** `POST /customers/{customer_id}/bookings/{booking_id}/checkout`

**Path Parameters:**
- `customer_id` (string): Unique customer identifier
- `booking_id` (string): Unique booking identifier

**Success Response:** `200 OK`
```json
{
  "id": "booking789",
  "checked_out": true,
  "message": "Bags checked out successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Booking not checked in or already checked out
- `404 Not Found`: Customer or booking not found
- `403 Forbidden`: Booking doesn't belong to the customer

---

## 📋 Data Models

### Customer Model
```json
{
  "id": "string",           // Auto-generated UUID
  "name": "string",         // Customer's full name
  "email": "string",        // Customer's email (unique)
  "phone": "string|null",   // Customer's phone number (optional)
  "created_at": "datetime"  // Account creation timestamp
}
```

### Booking Model
```json
{
  "id": "string",           // Auto-generated UUID
  "created_at": "datetime", // Booking creation timestamp
  "bag_count": "integer",   // Number of bags to store
  "dropoff_time": "datetime", // When bags will be dropped off
  "pickup_time": "datetime",  // When bags will be picked up
  "is_paid": "boolean",     // Payment status
  "is_cancelled": "boolean", // Cancellation status
  "checked_in": "boolean",  // Check-in status
  "checked_out": "boolean", // Check-out status
  "stashpoint_id": "string", // ID of the stashpoint
  "customer_id": "string"   // ID of the customer
}
```

### Stashpoint Model (for reference)
```json
{
  "id": "string",           // Auto-generated UUID
  "name": "string",         // Stashpoint name
  "description": "string|null", // Description
  "address": "string",      // Physical address
  "postal_code": "string",  // Postal code
  "latitude": "float",      // Latitude coordinate
  "longitude": "float",     // Longitude coordinate
  "capacity": "integer",    // Maximum bag capacity
  "open_from": "time",      // Opening time (HH:MM)
  "open_until": "time"      // Closing time (HH:MM)
}
```

---

## 🔧 Error Handling

All API endpoints follow consistent error response formats:

### Standard Error Response
```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details if applicable"
  }
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `500 Internal Server Error`: Server error

---

## 📝 Usage Examples

### Creating a Customer and Booking Flow

1. **Create a customer:**
```bash
curl -X POST http://localhost:5001/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1234567890"
  }'
```

2. **Find available stashpoints:**
```bash
curl "http://localhost:5001/api/v1/stashpoints/availability?lat=51.5&lng=-0.1&dropoff=2024-06-01T10:00:00Z&pickup=2024-06-01T18:00:00Z&bag_count=2&radius_km=5"
```

3. **Create a booking:**
```bash
curl -X POST http://localhost:5001/api/v1/customers/a1b2c3d4e5f6/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "stashpoint_id": "stash456",
    "bag_count": 2,
    "dropoff_time": "2024-06-01T10:00:00Z",
    "pickup_time": "2024-06-01T18:00:00Z"
  }'
```

4. **Check booking status:**
```bash
curl http://localhost:5001/api/v1/customers/a1b2c3d4e5f6/bookings/booking789
```

---

## 🚀 Implementation Notes

### Current Status
- ✅ Customer and Booking models are defined in the codebase
- ❌ Customer API endpoints are **NOT YET IMPLEMENTED**
- ❌ Authentication/authorization is not implemented
- ❌ Payment processing is not implemented

### Required Implementation
To implement these endpoints, you would need to:

1. Create a new blueprint file: `app/routes/customers.py`
2. Add validation utilities for customer data
3. Implement proper error handling
4. Add the customer blueprint to the main app
5. Create database migrations if needed
6. Add comprehensive tests

### Security Considerations
In a production environment, consider:
- Authentication (JWT tokens, OAuth, etc.)
- Authorization (customers can only access their own data)
- Rate limiting
- Input validation and sanitization
- HTTPS enforcement
- Data privacy compliance (GDPR, etc.)

---

*This documentation is based on the existing data models in the stasher-city/api codebase. The actual endpoints would need to be implemented following Flask best practices and the existing code structure.*