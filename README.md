# 🔍 Automated Job Application Finder & Scraper (Local & Secure)

A powerful, **locally run** job automation system that scrapes jobs from **Indeed, LinkedIn, Glassdoor, Naukri, Internshala, and more**. It runs entirely on your device (including Android tablets via **Termux**), ensuring complete privacy and control. Integrates directly with a local **n8n** workflow to process jobs and send them to you.

## 🚀 Key Features

- **🛡️ 100% Local**: Runs on your machine (Mac, Windows, Linux, Android/Termux). No cloud costs.
- **🌐 Multi-Site Scraping**: Hunts jobs across global & regional platforms (Indeed, LinkedIn, Glassdoor, Naukri, Internshala, Bayt, etc.).
- **🤖 Automated Workflows**: Connects to a local n8n instance to filter, process, and email results automatically.
- **📱 Android/Termux Ready**: Optimized for low-resource environments (runs smoothly on 4GB RAM tablets).
- **🔎 Smart Filtering**: Filters by location, remote status, job type (internship/full-time), and recency.
- **💾 Auto-Backup**: Saves all job data locally as JSON files instantly.
- **📧 Easy Alerts**: Uses standard SMTP (Zoho, Gmail, Outlook) for reliable email notifications.

## 📋 Supported Job Sites

| Site | Region | Best For |
|------|--------|----------|
| **Indeed** | Global | High volume, fast scraping |
| **LinkedIn** | Global | Professional roles (rate limited) |
| **Glassdoor** | Global | Jobs + company insights |
| **Google Jobs** | Global | Aggregated listings |
| **Naukri** | 🇮🇳 India | IT & Tech jobs |
| **Internshala** | 🇮🇳 India | Internships & Freshers |
| **ZipRecruiter** | 🇺🇸 USA | US-based roles |
| **Bayt** | 🌍 MENA | Middle East jobs |

## 🛠️ Tech Stack

- **Python (Flask)**: Core API server for scraping logic.
- **JobSpy**: Powerful job scraping library (integrated as local module).
- **n8n (Self-Hosted)**: Workflow orchestration tool.
- **Ngrok**: For secure local tunneling (optional).

## 🔧 How JobSpy Integration Works

This project uses **[JobSpy](https://github.com/Bunsly/JobSpy)** - a Python library for scraping job postings from multiple job boards.

### Integration Approach

Instead of installing JobSpy as a pip package, we integrate it **directly as a local module** (`JobSpy-main_new/`):

```python
# In server.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'JobSpy-main_new'))
from jobspy import scrape_jobs
```

**Why this approach?**
- ✅ **Full Control**: Customize JobSpy's behavior if needed
- ✅ **Version Lock**: No breaking changes from package updates
- ✅ **Offline Deploy**: Works in restricted environments (Railway, Termux)
- ✅ **Dependencies Bundled**: All requirements in one `requirements.txt`

### What JobSpy Does

JobSpy handles all the heavy lifting:
1. **Multi-site scraping** - Connects to Indeed, LinkedIn, Glassdoor, etc.
2. **Data normalization** - Returns consistent job data structure
3. **Smart filtering** - Applies location, job type, and recency filters
4. **Rate limit handling** - Manages request timing per site

### Our Wrapper Layer

The Flask server (`server.py`) acts as a **clean REST API wrapper** around JobSpy:
- Accepts simple JSON parameters
- Maps them to JobSpy's function signature
- Returns cleaned, JSON-serialized results
- Handles errors gracefully

**Example Flow:**
```
User/n8n → POST /job-search → Flask API → JobSpy Library → Job Sites → Results
```

### Supported Sites via JobSpy

JobSpy currently supports these platforms:
- Indeed, LinkedIn, Glassdoor, Google Jobs (Global)
- ZipRecruiter (USA/Canada)
- Naukri, Internshala (India)
- Bayt (Middle East)
- BDJobs (Bangladesh)

---

## ⚡ Quick Start

### 1. Installation

```bash
# Manual install
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python server.py
# Server starts on http://localhost:5000
```

### 3. Usage with n8n

Create an HTTP Request node in n8n sending a POST request to `http://localhost:5000/job-search` (or your Ngrok URL) with this JSON body:

```json
{
  "SEARCH_TERM": "python developer",
  "LOCATION": "India",
  "HOURS_OLD": 72,
  "JOB_TYPE": "internship",
  "IS_REMOTE": true
}
```

### 4. Android (Termux) Setup (Optional - For Testing)

**Note:** The Termux setup is **optional** and was used for testing on an old Android device. It's **not necessary** for production use.

For production, it's recommended to:
- Deploy Flask server on **Railway** (free cloud hosting)
- Run n8n locally on your main computer or use n8n Cloud

If you still want to experiment with Termux, see [TERMUX_SETUP.md](TERMUX_SETUP.md) for details.

---

## ⚙️ Configuration

No `.env` file required! All parameters are passed directly via the API.

### API Parameters (POST /job-search)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SEARCH_TERM` | string | required | Main search keywords |
| `LOCATION` | string | required | City, country, or "Remote" |
| `HOURS_OLD` | int | 72 | Max age of job postings in hours |
| `JOB_TYPE` | string | null | `fulltime`, `internship`, `parttime`, `contract` |
| `IS_REMOTE` | boolean| false | Set true to filter remote only |
| `DEFAULT_COUNTRY` | string | India | Country for Indeed/Glassdoor |
| `GOOGLE_SEARCH_TERM`| string | null | Specific phrase for Google Jobs |
| `INTERNSHALA_SEARCH_TERM` | string | null | Slug for Internshala (e.g. `software-development`) |

---

## 📂 Output

### n8n Payload
```json
{
  "success": true,
  "jobs": [
    {
      "title": "Software Developer Intern",
      "company": "Tech Company",
      "location": "Bangalore, India",
      "job_url": "https://...",
      "site": "linkedin"
    }
  ]
}
```

---

## 📜 Credits & License

**Built with ❤️ by [Punya Jain](https://github.com/punyajain1)**

Special thanks to **[JobSpy](https://github.com/Bunsly/JobSpy)** for providing the amazing job scraping library that powers this automation.

---

## 🤝 Contributing

Feel free to submit issues and pull requests!
