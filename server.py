from flask import Flask, request, jsonify
import os
import json
import sys
from datetime import datetime, date
import pandas as pd

# Add JobSpy to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JobSpy-main_new'))

# Import JobSpy
from jobspy import scrape_jobs

app = Flask(__name__)

def json_serial(obj):
    """JSON serializer for objects not serializable by default"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Job Scraper Server is running'
    }), 200

@app.route('/job-search', methods=['POST'])
def job_search():
    """
    Receive job search parameters, scrape jobs, and return results
    Accepts: SEARCH_TERM, LOCATION, GOOGLE_SEARCH_TERM, HOURS_OLD, 
             DEFAULT_COUNTRY, JOB_TYPE, IS_REMOTE, INTERNSHALA_SEARCH_TERM
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required parameters
        if 'SEARCH_TERM' not in data or not data['SEARCH_TERM']:
            return jsonify({
                'success': False,
                'message': 'SEARCH_TERM is required'
            }), 400
        
        if 'LOCATION' not in data or not data['LOCATION']:
            return jsonify({
                'success': False,
                'message': 'LOCATION is required'
            }), 400
        
        # Set defaults for hardcoded parameters
        results_wanted = 100
        distance = 50
        verbose = 1
        linkedin_fetch = True
        
        # Parse parameters directly
        search_term = data['SEARCH_TERM']
        location = data['LOCATION']
        country = data.get('DEFAULT_COUNTRY', 'India')
        hours_old = int(data.get('HOURS_OLD', 72))
        
        # Handle IS_REMOTE as both boolean and string
        is_remote_val = data.get('IS_REMOTE', False)
        if isinstance(is_remote_val, bool):
            is_remote = is_remote_val
        else:
            is_remote = str(is_remote_val).lower() == 'true'
        
        # Handle JOB_TYPE - convert "all" or empty string to None
        job_type_val = data.get('JOB_TYPE', '')
        if job_type_val and str(job_type_val).lower() not in ['all', 'none', '']:
            job_type = job_type_val
        else:
            job_type = None
        
        google_search_term = data.get('GOOGLE_SEARCH_TERM', '') or None
        internshala_search_term = data.get('INTERNSHALA_SEARCH_TERM', '') or None
        
        # Define sites based on location
        ALL_SITES = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter", "naukri", "internshala", "bdjobs", "bayt"]
        current_sites = ALL_SITES.copy()
        
        is_india = 'India' in location or country == 'India'
        is_us_canada = country in ['USA', 'Canada'] or any(x in location for x in ['United States', 'USA', 'US', 'Canada'])
        is_bangladesh = 'Bangladesh' in location or country == 'Bangladesh'
        
        # Filter sites by region
        if not is_us_canada and 'zip_recruiter' in current_sites:
            current_sites.remove('zip_recruiter')
        
        if is_india:
            if 'bdjobs' in current_sites:
                current_sites.remove('bdjobs')
        else:
            if 'naukri' in current_sites:
                current_sites.remove('naukri')
            if 'internshala' in current_sites:
                current_sites.remove('internshala')
        
        if not is_bangladesh and 'bdjobs' in current_sites:
            current_sites.remove('bdjobs')
        
        # Scrape jobs
        print(f"🔍 Scraping: {search_term} in {location}")
        print(f"   Sites: {', '.join(current_sites)}")
        
        jobs = scrape_jobs(
            site_name=current_sites,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location,
            distance=distance,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country,
            job_type=job_type,
            is_remote=is_remote,
            linkedin_fetch_description=linkedin_fetch,
            internshala_search_term=internshala_search_term,
            verbose=verbose,
        )
        
        if len(jobs) == 0:
            return jsonify({
                'success': True,
                'message': 'No jobs found',
                'timestamp': datetime.now().isoformat(),
                'search_term': search_term,
                'location': location,
                'total_jobs': 0,
                'jobs': []
            }), 200
        
        # Convert DataFrame to dict
        jobs_data = jobs.to_dict('records')
        
        # Clean the data
        cleaned_jobs = []
        for job in jobs_data:
            cleaned_job = {}
            for key, value in job.items():
                if isinstance(value, (datetime, date)):
                    cleaned_job[key] = value.isoformat()
                elif pd.isna(value):
                    cleaned_job[key] = None
                else:
                    cleaned_job[key] = value
            cleaned_jobs.append(cleaned_job)
        
        print(f"✅ Found {len(cleaned_jobs)} jobs")
        
        # Return the scraped data directly
        return jsonify({
            'success': True,
            'message': f'Successfully scraped {len(cleaned_jobs)} jobs',
            'timestamp': datetime.now().isoformat(),
            'search_term': search_term,
            'location': location,
            'total_jobs': len(cleaned_jobs),
            'sites_searched': current_sites,
            'jobs': cleaned_jobs
        }), 200
    
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
if __name__ == '__main__':
    print("🚀 Job Scraper Server Starting...")
    print("\n📖 Available Endpoints:")
    print("   GET    /health        - Health check")
    print("   POST   /job-search    - Scrape jobs and return results")
    print("\n🌐 Server running on http://localhost:5000\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
