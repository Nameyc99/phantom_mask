# Response
This project is a pharmacy transaction backend system designed to manage and analyze mask purchases across multiple pharmacies.
The system is built using **Django**, **Django REST Framework (DRF)** with **MySQL** as database.

## A. Required Information
### A.1. Requirement Completion Rate
- [x] List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at **PharmacyOpenAtTimeView** API.
- [x] List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at **PharmacyMaskListView** API.
- [x] List all pharmacies with more or less than x mask products within a price range.
  - Implemented at **PharmaciesMaskCountFilterView** API.
- [x] The top x users by total transaction amount of masks within a date range.
  - Implemented at **TopUsersByTransactionAmountView** API.
- [x] The total number of masks and dollar value of transactions within a date range.
  - Implemented at **TotalMaskSoldView** API.
- [x] Search for pharmacies or masks by name, ranked by relevance to the search term.
  - Implemented at **SearchView** API.
- [x] Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
  - Implemented at **PurchaseView** API.
### A.2. API Document
Access the full API reference via [Swagger UI](http://localhost:8000/api/docs/).

### A.3. Import Data Commands
Please run below at the root of the project to migrate data to database.

```bash
python manage.py migrate
python manage.py load_initial_data
```
## B. Bonus Information

### B.1. Test Coverage Report

I wrote down the 40 unit tests for the APIs I built. Please check the test coverage report at [here](https://cheerful-vacherin-b50dd6.netlify.app/).

You can run the test script by using the command below:

```bash
python manage.py test core.test.test_views
```


### B.2. Dockerized

Docker configurations (Dockerfile and docker-compose.yml) are included.

To build and run the project with Docker locally, use:

```bash
docker-compose build
docker-compose up -d
```

To run database migrations and import data inside the container:

```bash=
docker-compose exec web bash

python manage.py migrate
python manage.py load_initial_data
```

### B.3. Demo Site Url



## C. Other Information

### C.1. ERD

My ERD [erd-link](./ERD.pdf).

### C.2. Local Setup Instruction

For setting up project locally, please refer to this [link](./setup.md)

### C.3. Technical Document
For frontend programmer reading, please check this [technical document](./API.md) to know how to operate those APIs.

### C.4. Directory Structure
```
phantom_mask
├── core
│   ├── __init__.py
│   ├── admin.py
│   ├── API.md
│   ├── apps.py
│   ├── management
│   │   ├── __init__.py
│   │   └── commands
│   │       ├── __init__.py
│   │       └── load_initial_data.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── test
│   │   └── test_views.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── data
│   ├── pharmacies.json
│   └── users.json
├── docker-compose.yml
├── Dockerfile
├── ERD.pdf
├── htmlcov
│   └── index.html
├── manage.py
├── phantom_mask
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
├── requirements.txt
├── response.md
└── setup.md