from django.shortcuts import render
from datetime import datetime
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def home(request):
    job_file_path = BASE_DIR / 'dashboard' / 'data' / 'jobs.json'
    if job_file_path.exists():
        with open(job_file_path, 'r') as f:
            all_jobs = json.load(f)
        last_updated = datetime.fromtimestamp(os.path.getmtime(job_file_path)).strftime("%d %B %Y, %H:%M")
    else:
        all_jobs = []
        last_updated = "N/A"

    search_query = request.GET.get('search', '').lower()
    selected_category = request.GET.get('category')

    filtered_jobs = [
        job for job in all_jobs
        if (not selected_category or job.get('category') == selected_category)
        and (search_query in job.get('title', '').lower() or search_query in job.get('company', '').lower())
    ]

    tabs = [
        "Summer Internships",
        "Spring Weeks",
        "Off-Cycle Internships",
        "Industrial Placements",
        "Graduate Programmes",
        "Pre-University",
        "Events"
    ]

    return render(request, 'dashboard/index.html', {
        'jobs': filtered_jobs,
        'tabs': tabs,
        'last_updated': last_updated,
        'request': request
    })