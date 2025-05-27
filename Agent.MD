# Campaign Manager Development Instructions (Agents.md)

## Project Overview

### What We Want to Achieve
Build a web-based admin interface for managing promotional campaigns for a **Dash product scanner application**. The system should allow non-technical users to upload campaign images and schedule promotional periods without manual server file management.

### Current System (DO NOT MODIFY)
- **Existing Dash App**: Product scanner running on server (port 99)
- **File Location**: `/assets/` directory with date-based folders (`yyyy-mm-dd` format)
- **Image Requirements**: Each folder contains 3 specific images:
  - Background image: `{date}bkg.png`
  - Logo image: `{date}logo.png` 
  - Screensaver image: `{date}screensaver_bkg.png`
- **Auto-Selection Logic**: Python function `get_newest_folder()` automatically selects the most recent folder
- **Database**: Existing SQLite database for products (separate from campaign management)

## Project Structure

### Backend (Flask) - `C:\Development\campaign-manager\`
```
campaign-manager/
├── app.py                    # Main Flask application
├── config.py                # Configuration (JWT secrets, upload paths, DB settings)
├── models.py                # SQLAlchemy models (users, campaigns, images, logs)
├── requirements.txt          # Flask, JWT, SQLAlchemy, Pillow, etc.
├── .env                     # Environment variables
├── auth/
│   ├── routes.py            # Login, set-password, logout endpoints
│   ├── jwt_handler.py       # JWT token creation/validation
│   └── decorators.py        # @jwt_required, @log_activity decorators
├── api/
│   ├── campaigns.py         # CRUD operations for campaigns
│   ├── uploads.py           # File upload handling + folder creation
│   ├── users.py             # User management (admin only)
│   └── utils.py             # Helper functions
├── database/
│   ├── db_setup.py          # Database initialization script
│   └── migrations.sql       # Database schema creation
└── scripts/
    └── setup_admin.py       # Script to create first admin user
```

### Frontend (React) - `C:\Development\campaign-manager\campaign-manager-frontend\`
```
campaign-manager-frontend/
├── src/
│   ├── components/
│   │   ├── auth/            # Login, SetPassword, ProtectedRoute
│   │   ├── campaigns/       # Campaign list, form, card, image upload
│   │   ├── users/           # User management (admin only)
│   │   ├── logs/            # Activity logs display
│   │   └── common/          # Reusable UI components
│   ├── services/
│   │   ├── api.js           # Axios setup with JWT interceptors
│   │   ├── auth.js          # Authentication service
│   │   └── campaigns.js     # Campaign API calls
│   ├── context/
│   │   ├── AuthContext.jsx  # Authentication state management
│   │   └── AppContext.jsx   # Application state management
│   └── pages/               # Main page components
```

## Database Schema Requirements

### Core Tables
1. **users** - Authorized email addresses, password hashes, admin status
2. **campaigns** - Campaign details, dates, status, folder paths
3. **campaign_images** - Image metadata and file paths
4. **activity_logs** - Complete audit trail of all actions
5. **jwt_blacklist** - Revoked tokens for security

### Key Relationships
- Users create/update campaigns (foreign key tracking)
- Campaigns have 3 images (one-to-many relationship)
- All actions logged with user_id and timestamps

## Authentication System Requirements

### User Flow
1. **Authorized emails only** - Admin pre-adds email addresses to database
2. **First-time login** - Users with authorized emails set their password
3. **JWT tokens** - 8-hour expiration, blacklist on logout
4. **Activity logging** - Every action tracked with user, timestamp, IP

### Security Features
- Bcrypt password hashing
- JWT token validation on all protected routes
- Token blacklisting for secure logout
- Input validation and file upload security

## Core Features to Implement

### 1. Campaign Management
- **Create campaigns** with name, start date, end date
- **Upload 3 images** (background, logo, screensaver) with drag-and-drop
- **Preview functionality** showing how campaign will look
- **Status tracking** (scheduled, active, expired) based on dates
- **Edit/delete campaigns** with proper permission checking

### 2. File Management Integration
- **Automatic folder creation** in existing `/assets/` directory
- **Date-based naming** following `yyyy-mm-dd` format
- **Image renaming** to match Python script expectations
- **File validation** (size, type, dimensions)
- **Cleanup** when campaigns are deleted

### 3. User Management (Admin Only)
- **Add authorized emails** to system
- **View user activity** and login history
- **Deactivate users** when needed
- **Force password reset** for users

### 4. Activity Logging
- **Complete audit trail** of all system actions
- **User attribution** for every change
- **Filterable logs** by user, date, action type
- **Export capabilities** for compliance

## API Endpoints Required

### Authentication
- `POST /auth/login` - Email/password authentication
- `POST /auth/set-password` - First-time password setup
- `POST /auth/logout` - Token invalidation
- `GET /auth/verify` - Token validation

### Campaigns
- `GET /api/campaigns` - List all campaigns with status
- `POST /api/campaigns` - Create new campaign + folder structure
- `PUT /api/campaigns/{id}` - Update campaign details
- `DELETE /api/campaigns/{id}` - Delete campaign + cleanup files
- `POST /api/campaigns/{id}/upload` - Upload campaign images

### Users (Admin only)
- `GET /api/users` - List authorized users
- `POST /api/users` - Add new authorized email
- `PUT /api/users/{id}` - Update user status

### Logs
- `GET /api/logs` - Activity logs with filtering

## Integration Points

### With Existing Python Script
- **File structure compatibility** - Must match `get_newest_folder()` expectations
- **No code changes required** - Existing Dash app continues working unchanged
- **Asset directory** - Use existing `/assets/` folder structure
- **Naming conventions** - Exact file naming as currently expected

### Configuration Requirements
- **Upload path** - Point to existing assets directory
- **Database location** - Separate from existing product database
- **Port configuration** - Flask on 5000, Dash remains on 99
- **CORS setup** - Allow frontend domain access

## Implementation Strategy

### Phase 1: Backend Foundation
1. Set up Flask project structure
2. Create database models and migration scripts
3. Implement JWT authentication system
4. Create user management endpoints
5. Set up activity logging

### Phase 2: Campaign Management
1. Implement campaign CRUD operations
2. Build file upload system with validation
3. Create folder structure automation
4. Add campaign status logic
5. Test integration with existing assets folder

### Phase 3: Frontend Core
1. Set up React project with routing
2. Implement authentication components
3. Create campaign management interface
4. Build image upload with preview
5. Add user management (admin only)

### Phase 4: Integration & Polish
1. Connect frontend to backend APIs
2. Implement activity logging display
3. Add error handling and loading states
4. Test complete user workflows
5. Deploy and configure production settings

## Technical Specifications

### Backend Technologies
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT token management
- **Pillow** - Image processing and validation
- **Bcrypt** - Password hashing

### Frontend Technologies
- **React** - UI framework
- **React Router** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Styling (consistent with existing prototype)
- **Lucide React** - Icons

### Development Environment
- **Backend Port**: 5000 (Flask development server)
- **Frontend Port**: 5173 (Vite development server)
- **Database**: SQLite for development, configurable for production
- **File Storage**: Local filesystem (existing assets directory)

## Security Considerations

### File Upload Security
- Validate file types (images only)
- Check file sizes (prevent large uploads)
- Sanitize filenames
- Prevent path traversal attacks

### Authentication Security
- Strong password requirements
- JWT token expiration and refresh
- Token blacklisting on logout
- Rate limiting for login attempts

### API Security
- Input validation on all endpoints
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration for allowed origins
- Activity logging for audit trails

## Success Criteria

### Functional Requirements
1. ✅ Non-technical users can create campaigns without server access
2. ✅ Image uploads automatically create proper folder structure
3. ✅ Existing Python script continues working without modification
4. ✅ Campaign scheduling works with automatic status updates
5. ✅ Complete activity logging for all user actions
6. ✅ Secure authentication with authorized emails only

### Performance Requirements
1. Image upload handling for files up to 16MB
2. Fast campaign list loading with pagination
3. Responsive UI for tablet/mobile use
4. Efficient database queries with proper indexing

### Security Requirements
1. JWT-based authentication with token expiration
2. Activity logging for compliance and auditing
3. File upload validation and security
4. User permission management (admin vs regular users)

---

## Development Best Practices & Code Standards

### Python/Flask Backend Standards
1. **File Size Limit**: Maximum 200 lines per file
2. **Modular Design**: Single responsibility principle - one class/function per purpose
3. **Clean Code Practices**:
   - Descriptive variable and function names
   - Type hints where applicable
   - Docstrings for all functions and classes
   - Error handling with proper exceptions
   - Consistent formatting (follow PEP 8)

4. **File Organization**:
   - Keep models separate (max 3-4 models per file)
   - Split large route files by functionality
   - Use blueprints for route organization
   - Separate utilities into focused modules

5. **Error Handling**:
   - Custom exception classes
   - Proper HTTP status codes
   - Consistent error response format
   - Logging for debugging

### React/Frontend Standards
1. **Component Size**: Maximum 200 lines per component
2. **Component Design**:
   - Single responsibility per component
   - Custom hooks for reusable logic
   - Separate container and presentation components
   - Props validation with PropTypes or TypeScript

3. **File Organization**:
   - One component per file
   - Related components grouped in folders
   - Separate hooks, services, and utilities
   - Consistent naming conventions (PascalCase for components)

4. **State Management**:
   - Use Context API efficiently
   - Keep state as local as possible
   - Separate business logic from UI logic
   - Use custom hooks for complex state logic

5. **Performance Considerations**:
   - Lazy loading for routes
   - Memoization where appropriate
   - Optimize re-renders
   - Handle loading and error states

### Code Quality Standards

#### Backend Code Structure Example:
```python
# models/user.py (under 200 lines)
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """User model with validation and business logic."""
    
    def validate_email(self) -> bool:
        """Validate email format."""
        pass
    
    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        pass
```

#### Frontend Component Structure Example:
```jsx
// components/campaigns/CampaignCard.jsx (under 200 lines)
import React from 'react';
import { useCampaign } from '../../hooks/useCampaign';
import { formatDate } from '../../utils/formatters';

const CampaignCard = ({ campaign, onEdit, onDelete }) => {
  // Component logic here (max 200 lines)
  return (
    // JSX here
  );
};

export default CampaignCard;
```

### Modularization Guidelines

#### Backend Modularization:
- **models/**: Split by entity (users.py, campaigns.py, logs.py)
- **api/**: Split by resource (auth_routes.py, campaign_routes.py)
- **services/**: Business logic (auth_service.py, file_service.py)
- **utils/**: Pure functions (validators.py, formatters.py)

#### Frontend Modularization:
- **components/**: Split by feature and responsibility
- **hooks/**: Custom hooks for reusable logic
- **services/**: API calls and external integrations
- **utils/**: Pure utility functions
- **context/**: State management contexts

### Testing Standards
1. **Backend**: Unit tests for services, integration tests for APIs
2. **Frontend**: Component tests, hook tests, utility function tests
3. **Coverage**: Aim for 80%+ code coverage
4. **Test Organization**: Mirror source code structure

### Documentation Standards
1. **README files**: For each major module
2. **API Documentation**: Clear endpoint descriptions
3. **Component Documentation**: Props and usage examples
4. **Code Comments**: Explain why, not what

## Project Structure Status
✅ **Backend structure created** at `C:\Development\campaign-manager\`
✅ **Frontend structure created** at `C:\Development\campaign-manager\campaign-manager-frontend\`

All necessary folders and empty files are in place. Ready for implementation following the above standards.