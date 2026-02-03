#Using it Earliler when i was just figuring out how can i build this scraper it was just a file using webhooks to trigger the job scraping

#Now i have made it more modular and added server.py to handle the webhooks and job_scraper_webhook.py to handle the scraping logic


import urllib3
import ssl
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# SSL fix for macOS compatibility
try:
    urllib3.util.ssl_.DEFAULT_CIPHERS = 'DEFAULT@SECLEVEL=1'
    import ssl
    _original_create_default_context = ssl.create_default_context
    
    def _create_relaxed_context(purpose=ssl.Purpose.SERVER_AUTH, *, cafile=None, capath=None, cadata=None):
        context = _original_create_default_context(purpose, cafile=cafile, capath=capath, cadata=cadata)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        return context
    
    ssl.create_default_context = _create_relaxed_context
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception as e:
    print(f"⚠️ SSL fix failed: {e}")

# Use local JobSpy folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JobSpy-main_new'))
from jobspy import scrape_jobs

def scrape_jobs_simple(search_term, location, site_name, results_wanted, 
                       hours_old, country_indeed, internshala_search_term, google_search_term,
                       job_type, is_remote, distance, verbose, linkedin_fetch_description):
    """
    Scrape jobs from multiple sites
    
    Parameters:
    - google_search_term: Specific search term for Google Jobs (requires exact syntax)
    - job_type: fulltime, parttime, internship, contract
    - is_remote: Filter for remote jobs only
    - distance: Distance in miles from location
    """
    
    try:
        # Scrape jobs with all parameters
        jobs = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location,
            distance=distance,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country_indeed,
            job_type=job_type,
            is_remote=is_remote,
            linkedin_fetch_description=linkedin_fetch_description,
            internshala_search_term=internshala_search_term,
            verbose=verbose,
        )
        
        if len(jobs) == 0:
            print("❌ No jobs found. Try different search terms.")
            return
        
        # Show breakdown by site - ONLY THIS LOG
        if 'site' in jobs.columns:
            site_counts = jobs['site'].value_counts()
            print("\n📊 Jobs fetched per site:")
            for site, count in site_counts.items():
                print(f"   {site}: {count} jobs")
            
            # Show which sites returned no jobs
            missing_sites = set(site_name) - set(site_counts.index)
            if missing_sites:
                print(f"   {', '.join(missing_sites)}: 0 jobs")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        from importlib.metadata import version
        print(f"📦 JobSpy Version: {version('python-jobspy')}")
    except:
        pass

    # Use all available sites by default
    # Core sites: indeed, linkedin, glassdoor, google
    # Regional sites: zip_recruiter (US/Canada), naukri/internshala (India), bdjobs (Bangladesh)
    # International extras: bayt (Middle East - searches internationally)
    ALL_SITES = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter", "naukri", "internshala", "bdjobs", "bayt"]
    DEFAULT_SITES = ALL_SITES.copy()
    
    DEFAULT_WANTED = 100
    DEFAULT_HOURS = 72  # Hardcoded to 72 hours
    # country_indeed expects Title Case (e.g. 'India', 'USA', 'UK')
    DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "India")
    
    # Optional: Pre-set search term and location from env
    ENV_SEARCH_TERM = os.getenv("SEARCH_TERM", "")
    ENV_LOCATION = os.getenv("LOCATION", "")
    
    # Google-specific search term (required for Google Jobs to work properly)
    ENV_GOOGLE_SEARCH_TERM = os.getenv("GOOGLE_SEARCH_TERM", "")
    
    # Internshala specific search term (optional)
    ENV_INTERNSHALA_SEARCH_TERM = os.getenv("INTERNSHALA_SEARCH_TERM", "")
    
    # Job type and remote filters
    ENV_JOB_TYPE = os.getenv("JOB_TYPE", "")  # fulltime, parttime, internship, contract
    ENV_IS_REMOTE = os.getenv("IS_REMOTE", "false").lower() == "true"
    
    # Hardcoded advanced options for maximum performance
    ENV_DISTANCE = 50
    ENV_VERBOSE = 1
    ENV_LINKEDIN_FETCH_DESC = True

    # Parse Command Line Arguments
    import argparse
    parser = argparse.ArgumentParser(description="Job Spy Scraper")
    
    parser.add_argument("term", nargs="?", help="Search term (e.g. 'Software Engineer')")
    parser.add_argument("location", nargs="?", help="Location (e.g. 'San Francisco, CA')")
    parser.add_argument("--country", "-c", default=DEFAULT_COUNTRY, help=f"Indeed country code (default: {DEFAULT_COUNTRY})")
    parser.add_argument("--results", "-r", type=int, default=DEFAULT_WANTED, help=f"Results wanted per site (default: {DEFAULT_WANTED})")
    parser.add_argument("--hours", type=int, default=DEFAULT_HOURS, help=f"Fetch jobs from last X hours (hardcoded: {DEFAULT_HOURS})")
    
    args = parser.parse_args()

    # Interactive Mode if Arguments are Missing
    # Priority: CLI args > Environment variables > Interactive prompt
    if args.term:
        search_term = args.term
    elif ENV_SEARCH_TERM:
        search_term = ENV_SEARCH_TERM
    else:
        print("\n👋 Welcome to JobSpy Scraper!")
        search_term = input("   💼 Enter job role: ").strip()
        if not search_term:
            print("   ❌ Search term is required")
            sys.exit(1)

    if args.location:
        location = args.location
    elif ENV_LOCATION:
        location = ENV_LOCATION
    else:
        location = input("   🌍 Enter location: ").strip()
        if not location:
            print("   ❌ Location is required")
            sys.exit(1)
    
    # Normalize country code
    country_indeed = args.country
    country_map = {
        'INDIA': 'India',
        'USA': 'USA', 'US': 'USA', 'UNITED STATES': 'USA', 'AMERICA': 'USA',
        'UK': 'UK', 'UNITED KINGDOM': 'UK',
        'CANADA': 'Canada'
    }
    country_indeed = country_map.get(country_indeed.upper(), country_indeed)

    # Filter out region-specific job sites based on search location
    current_sites = list(DEFAULT_SITES)
    is_india_search = 'India' in location or 'India' in country_indeed or country_indeed == 'India'
    is_us_canada_search = country_indeed in ['USA', 'Canada'] or any(x in location for x in ['United States', 'USA', 'US', 'Canada'])
    is_bangladesh_search = 'Bangladesh' in location or country_indeed == 'Bangladesh'
    
    # ZipRecruiter: US/Canada only
    if not is_us_canada_search and 'zip_recruiter' in current_sites:
        current_sites.remove('zip_recruiter')
    
    # India-specific sites
    if is_india_search:
        if 'bdjobs' in current_sites:
            current_sites.remove('bdjobs')
    else:
        if 'naukri' in current_sites:
            current_sites.remove('naukri')
        if 'internshala' in current_sites:
            current_sites.remove('internshala')
    
    # Bangladesh-specific sites
    if not is_bangladesh_search and 'bdjobs' in current_sites:
        current_sites.remove('bdjobs')
    
    # Determine site-specific search terms
    internshala_search_term = ENV_INTERNSHALA_SEARCH_TERM if ENV_INTERNSHALA_SEARCH_TERM else None
    google_search_term = ENV_GOOGLE_SEARCH_TERM if ENV_GOOGLE_SEARCH_TERM else None
    job_type = ENV_JOB_TYPE if ENV_JOB_TYPE else None

    # Scrape jobs
    scrape_jobs_simple(
        search_term=search_term, 
        location=location,
        site_name=current_sites,
        results_wanted=args.results,
        hours_old=args.hours,
        country_indeed=country_indeed,
        internshala_search_term=internshala_search_term,
        google_search_term=google_search_term,
        job_type=job_type,
        is_remote=ENV_IS_REMOTE,
        distance=ENV_DISTANCE,
        verbose=ENV_VERBOSE,
        linkedin_fetch_description=ENV_LINKEDIN_FETCH_DESC
    )