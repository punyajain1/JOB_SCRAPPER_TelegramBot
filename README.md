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
- **JobSpy**: Powerful scraping library (integrated directly, not as package).
- **n8n (Self-Hosted)**: Workflow orchestration tool.
- **Ngrok**: For secure local tunneling (optional).

## ⚡ Quick Start

### 1. Installation

```bash
# Automated install (Mac/Linux/Termux)
./install.sh

# OR Manual install
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

### 4. Android (Termux) Setup

See [TERMUX_SETUP.md](TERMUX_SETUP.md) for a detailed guide on running this entire stack on your Android device!

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

### Local Backup
Jobs are also saved locally as `jobs_YYYYMMDD_HHMM.json`

---

## 📜 Credits & License

**Built with ❤️ by [Punya Jain](https://github.com/punyajain1)**

Special thanks to **[JobSpy](https://github.com/Bunsly/JobSpy)** for providing the amazing job scraping library that powers this automation.

---

## 🤝 Contributing

Feel free to submit issues and pull requests!
