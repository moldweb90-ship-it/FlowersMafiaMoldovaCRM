# Overview

This is a Flower CRM system built with Flask that manages flower inventory, bouquet compositions, categories, and user management. The application helps flower businesses track their products, create bouquets with cost calculations, and manage pricing with markup and delivery costs. The system supports multi-user functionality with role-based access control and includes export capabilities for catalog data.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **Client-Side**: Vanilla JavaScript with jQuery for dynamic interactions
- **Styling**: Bootstrap CSS framework with Font Awesome icons and custom CSS
- **Mobile-First**: Responsive design with mobile navigation considerations

## Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Authentication**: Flask-Login with session-based authentication
- **Forms**: WTForms for form handling and validation
- **File Structure**: Modular approach with separate files for routes, models, and forms

## Data Storage Solutions
- **Primary Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **ORM**: SQLAlchemy with DeclarativeBase
- **Models**: User management, flowers, categories, bouquets, and compositions
- **Multi-tenancy**: Support for user-specific databases (DatabaseManager class)

## Authentication and Authorization
- **User Roles**: Admin and regular user roles with different permissions
- **User Status**: Pending, active, and suspended states for user approval workflow
- **Session Management**: Flask sessions with custom cookie settings for HTTP environments
- **Password Security**: Werkzeug password hashing for secure credential storage

## Core Business Logic
- **Inventory Management**: Flower catalog with pricing per unit
- **Bouquet Builder**: Dynamic composition system linking flowers with quantities
- **Pricing Engine**: Automatic cost calculation with markup percentages and delivery costs
- **Category System**: Hierarchical organization of bouquets by categories

## Export and Reporting
- **Excel Export**: OpenPyXL integration for formatted XLSX file generation
- **CSV Support**: Built-in CSV export functionality
- **Filtered Exports**: Category-based filtering for targeted data exports

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework with SQLAlchemy integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **SQLAlchemy**: Database ORM with PostgreSQL support
- **Werkzeug**: Password hashing and WSGI utilities

## UI and Frontend Libraries
- **Bootstrap 5**: CSS framework (served via CDN)
- **Font Awesome 6**: Icon library (served via CDN)
- **jQuery**: JavaScript library for DOM manipulation

## Data Processing Libraries
- **OpenPyXL**: Excel file generation with styling support
- **CSV**: Built-in Python module for CSV export functionality

## Database and Environment
- **PostgreSQL**: Primary database system (configured via DATABASE_URL)
- **Environment Variables**: DATABASE_URL for database connection configuration
- **ProxyFix**: Werkzeug middleware for handling proxy headers

## Development and Deployment
- **Replit Environment**: Configured for Replit hosting with appropriate session settings
- **Migration Support**: Database migration scripts for multi-user functionality
- **HTTP Configuration**: Session cookies configured for non-HTTPS environments