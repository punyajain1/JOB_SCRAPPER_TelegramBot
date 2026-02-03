# Job Scraper Server API Documentation

## Overview
REST API server for managing job scraper parameters and triggering scraping operations.

**Base URL:** `http://localhost:5000`

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the server is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Job Scraper Server is running"
}
```

---

### 2. Get All Parameters
**GET** `/parameters`

Retrieve all current parameters stored in the .env file.

**Response:**
```json
{
  "success": true,
  "parameters": {
    "WEBHOOK_URL": "https://...",
    "SEARCH_TERM": "Python Developer",
    "LOCATION": "New York",
    ...
  },
  "count": 13
}
```

---

### 3. Get Single Parameter
**GET** `/parameters/<key>`

Get a specific parameter value.

**Example:** `GET /parameters/SEARCH_TERM`

**Response:**
```json
{
  "success": true,
  "key": "SEARCH_TERM",
  "value": "Python Developer"
}
```

---

### 4. Set Multiple Parameters
**POST** `/parameters`

Update multiple parameters at once.

**Request Body:**
```json
{
  "SEARCH_TERM": "Software Engineer",
  "LOCATION": "San Francisco, CA",
  "IS_REMOTE": "true"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Updated 3 parameter(s)",
  "updated": ["SEARCH_TERM", "LOCATION", "IS_REMOTE"],
  "parameters": { ... }
}
```

---

### 5. Set Single Parameter
**PUT** `/parameters/<key>` or **POST** `/parameters/<key>`

Update a single parameter.

**Example:** `PUT /parameters/SEARCH_TERM`

**Request Body:**
```json
{
  "value": "Data Scientist"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Parameter \"SEARCH_TERM\" updated",
  "key": "SEARCH_TERM",
  "value": "Data Scientist"
}
```

---

### 6. Delete Single Parameter
**DELETE** `/parameters/<key>`

Remove a parameter from the .env file.

**Example:** `DELETE /parameters/GOOGLE_SEARCH_TERM`

**Response:**
```json
{
  "success": true,
  "message": "Parameter \"GOOGLE_SEARCH_TERM\" removed"
}
```

---

### 7. Delete Multiple Parameters
**POST** `/parameters/batch-delete`

Remove multiple parameters at once.

**Request Body:**
```json
{
  "keys": ["GOOGLE_SEARCH_TERM", "INTERNSHALA_SEARCH_TERM"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Removed 2 parameter(s)",
  "removed": ["GOOGLE_SEARCH_TERM", "INTERNSHALA_SEARCH_TERM"],
  "not_found": []
}
```

---

### 8. Trigger Job Scraping
**POST** `/scrape`

Start job scraping with current parameters. Optionally override parameters for this request only.

**Request Body (Optional):**
```json
{
  "SEARCH_TERM": "Frontend Developer",
  "LOCATION": "Austin, TX"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Job scraping completed",
  "parameters_used": {
    "search_term": "Frontend Developer",
    "location": "Austin, TX",
    "sites": ["indeed", "linkedin", "glassdoor", "google"],
    "results_wanted": 100,
    "hours_old": 72
  }
}
```

---

### 9. Reset Parameters
**POST** `/reset`

Reset all parameters to default values.

**Response:**
```json
{
  "success": true,
  "message": "Parameters reset to defaults",
  "parameters": { ... }
}
```

---

## Available Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `WEBHOOK_URL` | string | n8n webhook URL | Webhook endpoint for job data |
| `SEARCH_TERM` | string | - | Job title/keywords to search |
| `LOCATION` | string | - | Geographic location |
| `DEFAULT_COUNTRY` | string | India | Country code (India, USA, UK, etc.) |
| `GOOGLE_SEARCH_TERM` | string | - | Specific search for Google Jobs |
| `INTERNSHALA_SEARCH_TERM` | string | - | Specific search for Internshala |
| `JOB_TYPE` | string | - | fulltime, parttime, internship, contract |
| `IS_REMOTE` | boolean | false | Filter for remote jobs only |
| `RESULTS_WANTED` | integer | 100 | Number of results per site |
| `HOURS_OLD` | integer | 72 | Max age of jobs in hours |
| `DISTANCE` | integer | 50 | Search radius in miles |
| `VERBOSE` | integer | 1 | Logging verbosity (0-2) |
| `LINKEDIN_FETCH_DESC` | boolean | true | Fetch full LinkedIn descriptions |

---

## Usage Examples

### Using cURL

**Set parameters:**
```bash
curl -X POST http://localhost:5000/parameters \
  -H "Content-Type: application/json" \
  -d '{
    "SEARCH_TERM": "Python Developer",
    "LOCATION": "New York, NY",
    "IS_REMOTE": "true"
  }'
```

**Get all parameters:**
```bash
curl http://localhost:5000/parameters
```

**Delete a parameter:**
```bash
curl -X DELETE http://localhost:5000/parameters/GOOGLE_SEARCH_TERM
```

**Trigger scraping:**
```bash
curl -X POST http://localhost:5000/scrape
```

**Trigger with override:**
```bash
curl -X POST http://localhost:5000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "SEARCH_TERM": "DevOps Engineer",
    "LOCATION": "Seattle, WA"
  }'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Set parameters
response = requests.post(f"{BASE_URL}/parameters", json={
    "SEARCH_TERM": "Machine Learning Engineer",
    "LOCATION": "Boston, MA",
    "IS_REMOTE": "true",
    "RESULTS_WANTED": "50"
})
print(response.json())

# Trigger scraping
response = requests.post(f"{BASE_URL}/scrape")
print(response.json())

# Get parameters
response = requests.get(f"{BASE_URL}/parameters")
print(response.json())
```

### Using JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:5000";

// Set parameters
fetch(`${BASE_URL}/parameters`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    SEARCH_TERM: "Full Stack Developer",
    LOCATION: "Remote",
    IS_REMOTE: "true"
  })
})
  .then(res => res.json())
  .then(data => console.log(data));

// Trigger scraping
fetch(`${BASE_URL}/scrape`, { method: 'POST' })
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Running the Server

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python server.py
   ```

3. **Server will be available at:**
   ```
   http://localhost:5000
   ```

---

## Notes

- All parameters are automatically saved to the `.env` file
- Parameters persist across server restarts
- The `/scrape` endpoint temporarily overrides parameters without saving them
- Regional job sites are automatically filtered based on location
- All API responses follow JSON format with `success` boolean field
