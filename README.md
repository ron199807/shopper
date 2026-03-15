# Shopper Application

## Project Overview
The Shopper application is a modern e-commerce platform built with Django, allowing users to be a Client, Shopper or both. That allows a client to post a shopping list and shoppers can bid for the list and the owner(owner) of the list will offer the job of shopping to the shopper they choose. And the user who registers as both will be able to both post a list and they can also bid for the list.

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ron199807/shopper.git
   cd shopper
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database settings** in `settings.py` as per your local setup.

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** to access the admin panel:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the application**:
   ```bash
   python manage.py runserver
   ```

## Features
- User authentication and profiles
- Shopping list Listing
- Bding for the list and when we have a winner all the other bids will bemarked lost

## Technology Stack
- **Backend**: Django, Python
- **Database**: PostgreSQL (or SQLite for development)
- **Frontend**: Next.js, Tailwind css, TypeScript
- **Deployment**: Docker, AWS (for production)

## Project Structure
```
shopper/
├── shopper/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── app/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── templates/
├── manage.py
└── requirements.txt
``` 

## Usage Examples
- **Browsing Products**: Users can view all Shopping Lists on the landing page.
- **Biding**: only Shoppers/both can bid for the list.
- **Dashboards**: every user has a dashboard to monitor what is happening in realtime
