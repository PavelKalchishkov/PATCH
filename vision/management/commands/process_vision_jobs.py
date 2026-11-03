from django.core.management.base import BaseCommand

from vision.models import VisionJob, VisionJobStatus
from vision.pipeline import run_vision_job


class Command(BaseCommand):
    help = "Run queued computer-vision jobs in the foreground."

    def handle(self, *args, **options):
        jobs = VisionJob.objects.filter(status=VisionJobStatus.QUEUED)
        count = 0
        for job in jobs:
            run_vision_job(str(job.id))
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {count} job(s)."))
