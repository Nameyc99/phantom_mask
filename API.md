# 📘 Phantom Mask API Technical Document

This technical document is for frontend developers integrating with the Phantom Mask API. It covers API endpoints, request/response examples, and usage instructions.

---

## 🔐 Base URL

For local development: http://localhost:8000/api/


You can test APIs using curl, Postman, or Swagger UI at:
http://localhost:8000/api/docs/

---

## 📚 API Endpoints Overview

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/pharmacies/open/` | GET | Get pharmacies open at a given time/day |
| `/pharmacies/<id>/masks/` | GET | Get masks sold at a specific pharmacy |
| `/pharmacies/mask-count/` | GET | Filter pharmacies by number of mask types within price range |
| `/transactions/top-users/` | GET | Get top X users by transaction amount |
| `/transactions/summary/` | GET | Get total masks sold and transaction value in a date range |
| `/search/` | GET | Search pharmacies or masks by name |
| `/purchase/` | POST | Simulate a mask purchase by a user |

---

## 📌 Example Usage

### 1. List Pharmacies Open at Time

**GET** `/pharmacies/open/?day=Monday&time=14:30`

**Response**
```json
[
  {
    "id": 1,
    "name": "DFW Wellness",
    "cash_balance": "328.41",
    "created_at": "2025-05-27T10:24:47.923959Z"
  },
  {
    "id": 2,
    "name": "Carepoint",
    "cash_balance": "593.35",
    "created_at": "2025-05-27T10:24:47.961455Z"
  }
]
```

###  2. List Masks in a Pharmacy

**GET** `/pharmacies/1/masks/?sort=name or ?sort=price`

Response

```json
[
  {
    "id": 1,
    "name": "True Barrier (green) (3 per pack)",
    "price": "13.70",
    "pharmacy": 1
  }
]
```

### 3.  Filter Pharmacies by Mask Count in Price Range

**GET** `/pharmacies/mask-count/?min_price=5&max_price=10&operator=gte&count=2
`

Response
```json
[
  {
    "id": 1,
    "name": "DFW Wellness",
    "cash_balance": "328.41",
    "created_at": "2025-05-27T10:24:47.923959Z"
  },
  {
    "id": 9,
    "name": "Centrico",
    "cash_balance": "277.94",
    "created_at": "2025-05-27T10:24:48.187086Z"
  }
]
```

### 4.  Top X Users by Transaction Amount
**GET** /users/top/?end_date=2025-01-01&limit=10&start_date=2021-01-01

Response
```json
[
  {
    "id": 8,
    "name": "Timothy Schultz",
    "cash_balance": "221.03",
    "created_at": "2025-05-27T10:24:48.637286Z"
  },
  {
    "id": 4,
    "name": "Lester Arnold",
    "cash_balance": "154.97",
    "created_at": "2025-05-27T10:24:48.571931Z"
  }
]
```

### 5. Total Masks Sold & Value in Date Range
**GET** /transactions/summary/?end_date=2021-01-10&start_date=2021-01-01

```json
{
  "total_masks_sold": 26,
  "total_transaction_value": 465.76
}
```

### 6. Search Pharmacies or Masks
**GET** search/?query=Well&(optional: category=masks|pharmacies)
```json
{
  "masks": [],
  "pharmacies": [
    {
      "id": 1,
      "name": "DFW Wellness",
      "cash_balance": "328.41",
      "created_at": "2025-05-27T10:24:47.923959Z"
    },
    {
      "id": 4,
      "name": "Welltrack",
      "cash_balance": "507.29",
      "created_at": "2025-05-27T10:24:48.016905Z"
    }
  ]
}
```

### 7. Simulate a Purchase
POST /purchase/

Request Body
```json
{
  "user_id": 0,
  "purchases": [
    {
      "pharmacy_id": 0,
      "mask_id": 0,
      "quantity": 0
    }
  ]
}
```

Response
```json
[
  {
    "id": 0,
    "transaction_date": "2025-05-27T11:05:00.152Z",
    "transaction_amount": "17948745.9",
    "user": 0,
    "pharmacy": 0,
    "mask": 0
  }
]
```

