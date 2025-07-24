from django.core.management.base import BaseCommand
from dashboard.scraper import scrape_all

class Command(BaseCommand):
    help = 'Refresh job data from the Trackr scraper'

    def handle(self, *args, **kwargs):
        self.stdout.write('Refreshing job data...')
        jobs = scrape_all()
        self.stdout.write(self.style.SUCCESS(f'✓ {len(jobs)} jobs refreshed.'))
