## Setup Instructions

### 1. Local Setup

Follow these steps to run the project locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Nameyc99/phantom_mask.git
   cd phantom-masks

2. **Create and activate a Python virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    
4. Ensure MySQL is running and accessible using the credentials from your .env file
    ```
    MYSQL_DB=your_db_name
    MYSQL_USER=your_username
    MYSQL_PASSWORD=your_password
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    ```

4. **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Load initial data into the database:**
    
    ```bash
    python manage.py load_initial_data
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    
7. **Open your browser and visit:**
    http://localhost:8000

If you prefer using **PostgreSQL**, update your `.env` file and `settings.py` as shown below.

**`.env`:**
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=your_postgres_db
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

In phantom_mask/settings.py, replace or update the DATABASES section.
**`settings.py`:**

```
...other settings

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('POSTGRES_DB', os.getenv('MYSQL_DB')),
        'USER': os.getenv('POSTGRES_USER', os.getenv('MYSQL_USER')),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', os.getenv('MYSQL_PASSWORD')),
        'HOST': os.getenv('POSTGRES_HOST', os.getenv('MYSQL_HOST', 'localhost')),
        'PORT': os.getenv('POSTGRES_PORT', os.getenv('MYSQL_PORT', '3306')),
    }
}
```

💡 Make sure you have psycopg2 installed for PostgreSQL support:

```bash
pip install psycopg2-binary
```