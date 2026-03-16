# Hymart Platform (海贸特)

船舶行业全产业链综合服务平台 (Shipping Taobao/JD)

## Project Structure

- **apps/**: Django applications
  - **users**: User management (Buyers, Sellers, Service Providers, Crew)
  - **market**: Ship Trading Hub (New/Used ships, Chartering)
  - **store**: Maritime Mall (Parts, Supplies, Bunker)
  - **crew**: Crew Talent Port (Recruitment, Training)
  - **services**: Technical Services (Repairs, Inspections)
  - **core**: Shared utilities and base models
- **config/**: Project configuration
- **venv/**: Virtual environment

## Setup

1.  **Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install django djangorestframework django-cors-headers
    ```

2.  **Run**:
    ```bash
    python manage.py runserver
    ```

## Status
- [x] Project Initialized
- [x] Apps Created
- [x] Settings Configured (DRF, i18n, Apps)
- [x] Database Migrated
