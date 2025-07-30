"""Example usage of MCP Blarify Server tools."""

import asyncio
import json
from typing import Dict, Any


async def simulate_tool_call(tool_name: str, arguments: Dict[str, Any]):
    """Simulate calling an MCP tool."""
    print(f"\n=== Calling {tool_name} ===")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print("\n--- Example Response ---")
    
    if tool_name == "getContextForFiles":
        return """# Context for Files

## Directory: /src/services

### File: user_service.py
**Path**: `/src/services/user_service.py`

**Description**: Service for managing user data and authentication

**Contains**:
- CLASSs: UserService
- FUNCTIONs: create_user, get_user, update_user, delete_user

**Imports**:
- models.user
- utils.validation
- utils.security

**Imported by**:
- /src/api/routes/users.py
- /src/api/routes/auth.py
- /tests/services/test_user_service.py

### File: auth_service.py
**Path**: `/src/services/auth_service.py`

**Description**: Handles authentication and authorization logic

**Contains**:
- CLASSs: AuthService
- FUNCTIONs: login, logout, verify_token, refresh_token

**Imports**:
- jwt
- services.user_service
- models.token

**Imported by**:
- /src/api/routes/auth.py
- /src/middleware/auth_middleware.py
"""
    
    elif tool_name == "getContextForSymbol":
        return """# Symbol: UserService

**Type**: CLASS
**Location**: `/src/services/user_service.py`

**Description**: Core service for user management operations including CRUD operations, password management, and user validation.

**Inherits from**: BaseService
**Inherited by**: ExtendedUserService (in /src/services/extended_user.py)

**Methods**:
- create_user(user_data: dict) -> User
- get_user(user_id: int) -> Optional[User]
- update_user(user_id: int, user_data: dict) -> User
- delete_user(user_id: int) -> bool
- validate_password(user_id: int, password: str) -> bool
- reset_password(user_id: int, new_password: str) -> bool

**Called by**: 8 locations
- UserController.create in `/src/api/controllers/user_controller.py`
- UserController.get in `/src/api/controllers/user_controller.py`
- AuthService.login in `/src/services/auth_service.py`
- AuthService.register in `/src/services/auth_service.py`
- UserValidator.validate in `/src/validators/user_validator.py`

## Related Symbols

### UserController
**Type**: CLASS
**Location**: `/src/api/controllers/user_controller.py`
Uses UserService for all user operations
"""
    
    elif tool_name == "buildPlanForChange":
        return """# Implementation Plan

## Change Request
Add email verification to user registration process

## Impact Analysis
- **Entities Affected**: 4
- **Total Dependencies**: 12
- **Files to Modify**: 8
- **Test Files**: 5

## Implementation Steps

### 1. Prepare Development Environment
- Create feature branch: `feature/email-verification`
- Ensure all tests pass before starting
- Review existing code structure

### 2. Modify Existing Files

#### 1. Update `/src/models/user.py`
- Add `email_verified` boolean field (default: False)
- Add `verification_token` string field
- Add `verification_sent_at` timestamp field

#### 2. Update `/src/services/user_service.py`
- Modify `create_user` to generate verification token
- Add `verify_email(token: str) -> bool` method
- Add `resend_verification(user_id: int) -> bool` method

#### 3. Update `/src/services/email_service.py`
- Add `send_verification_email(user: User, token: str)` method
- Create email template for verification

#### 4. Update `/src/api/routes/auth.py`
- Add `/verify-email/<token>` endpoint
- Add `/resend-verification` endpoint
- Update registration response to indicate verification needed

### 3. Create New Components

#### 1. Create `/src/templates/email/verification.html`
- HTML template for verification email
- Include verification link and instructions

#### 2. Create `/src/utils/token_generator.py`
- Secure token generation utilities
- Token validation methods

### 4. Update Tests
Existing test files to update:
- `/tests/services/test_user_service.py`
- `/tests/services/test_email_service.py`
- `/tests/api/test_auth.py`
- `/tests/models/test_user.py`
- `/tests/integration/test_registration_flow.py`

### 5. Update Documentation
Documentation files to update:
- `/docs/api/authentication.md`
- `/docs/user-guide/registration.md`
- `/README.md` (mention email verification requirement)

### 6. Validation
- Run full test suite
- Test email delivery in development environment
- Verify token expiration logic
- Test edge cases (invalid tokens, expired tokens)

## Dependencies to Consider
- **UserService**: Add verification logic
- **EmailService**: Ensure SMTP configuration
- **User model**: Database migration required
- **AuthController**: Update registration flow

## Risk Assessment
- **Breaking Changes**: Existing users won't have email_verified field
- **Performance Impact**: Additional database queries for verification
- **Security**: Ensure tokens are cryptographically secure

## Rollback Plan
- Keep feature branch separate until fully tested
- Create database migration rollback script
- Document how to disable email verification if needed
"""
    
    else:
        return f"Unknown tool: {tool_name}"


async def main():
    """Run example tool calls."""
    print("MCP Blarify Server - Example Tool Usage")
    print("=" * 50)
    
    # Example 1: Get context for files
    response = await simulate_tool_call(
        "getContextForFiles",
        {
            "file_paths": [
                "src/services/user_service.py",
                "src/services/auth_service.py"
            ]
        }
    )
    print(response)
    
    # Example 2: Get context for a symbol
    response = await simulate_tool_call(
        "getContextForSymbol",
        {
            "symbol_name": "UserService",
            "symbol_type": "class"
        }
    )
    print(response)
    
    # Example 3: Build a plan for change
    response = await simulate_tool_call(
        "buildPlanForChange",
        {
            "change_request": "Add email verification to user registration process"
        }
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())