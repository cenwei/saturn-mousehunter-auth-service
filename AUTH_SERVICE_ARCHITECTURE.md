# Auth Service Architecture - Multi-User Authentication

## Overview
The auth service now supports both admin and regular user authentication with a complete multi-tier architecture.

## Fixed Issues

### 1. Virtual Environment Path
- **Before**: `VIRTUAL_ENV=/home/cenwei/workspace/saturn-mousehunter/.venv`
- **After**: `VIRTUAL_ENV=/home/cenwei/workspace/saturn_mousehunter/.venv`
- **Status**: ✅ Fixed

### 2. Multi-User Authentication Support
- **Before**: Only admin login supported
- **After**: Both admin and tenant user authentication
- **Status**: ✅ Complete

## Authentication Endpoints

### Admin Authentication
```
POST /api/v1/admin/users/login
```
- Purpose: System administrators
- Features: Full admin management capabilities

### Tenant User Authentication
```
POST /api/v1/users/login
```
- Purpose: Regular users (tenant users)
- Features: Multi-tenant user management

## Complete API Endpoints

### Admin Routes (`/api/v1/admin/users/`)
- `POST /login` - Admin login
- `POST /` - Create admin user
- `GET /me` - Get current admin profile
- `GET /{user_id}` - Get admin user details
- `PUT /{user_id}` - Update admin user
- `DELETE /{user_id}` - Delete admin user
- `GET /` - List admin users
- `POST /{user_id}/change-password` - Change password
- `POST /{user_id}/reset-password` - Reset password

### Tenant User Routes (`/api/v1/users/`)
- `POST /login` - Tenant user login
- `POST /` - Create tenant user
- `GET /me` - Get current tenant user profile
- `GET /{user_id}` - Get tenant user details
- `PUT /{user_id}` - Update tenant user
- `DELETE /{user_id}` - Delete tenant user
- `GET /` - List tenant users
- `GET /tenant/{tenant_id}` - List users by tenant
- `POST /{user_id}/change-password` - Change password
- `POST /{user_id}/reset-password` - Reset password

## Key Features

### Multi-Tenant Support
- Users belong to specific tenants
- Tenant-scoped operations and permissions

### Role-Based Access Control
- Admin users: System-level permissions
- Tenant users: Tenant-scoped permissions
- Permission-based route protection

### Security Features
- JWT-based authentication for both user types
- Password strength validation
- Audit logging for all operations
- IP and user agent tracking

### Architecture Components
- **Models**: Separate admin and tenant user models
- **Services**: Business logic for both user types
- **Repositories**: Data access layer
- **Dependencies**: Service injection and auth decorators
- **Routes**: RESTful API endpoints

## Usage

### Admin Login
```bash
curl -X POST http://localhost:8001/api/v1/admin/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Tenant User Login
```bash
curl -X POST http://localhost:8001/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "tenant-123", "username": "user", "password": "password"}'
```

## Files Modified

### New Files
- `src/api/routes/tenant_users.py` - Tenant user API routes

### Updated Files
- `src/main.py` - Added tenant routes registration
- `src/api/dependencies/services.py` - Added tenant user service dependencies

### Existing Files (Verified)
- `src/domain/models/auth_tenant_user.py` - Tenant user models
- `src/application/services/tenant_user_service.py` - Tenant user business logic
- `src/infrastructure/repositories/tenant_user_repo.py` - Data access
- `src/api/dependencies/auth.py` - Authentication dependencies

## Service Health
- Service URL: `http://localhost:8001`
- Health Check: `GET /health`
- API Documentation: `GET /docs`
- OpenAPI Spec: `GET /openapi.json`