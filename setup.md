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
