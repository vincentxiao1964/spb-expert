import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)

def crawl_news_job():
    """
    Job to run the crawl_news command.
    """
    print("Executing crawl_news_job...")
    call_command('crawl_news')

def crawl_sol_job():
    """
    Job to run the crawl_sol command.
    """
    print("Executing crawl_sol_job...")
    call_command('crawl_sol')

def crawl_eship_job():
    """
    Job to run the crawl_eship command.
    """
    print("Executing crawl_eship_job...")
    call_command('crawl_eship')

def crawl_horizon_job():
    """
    Job to run the crawl_horizon command.
    """
    print("Executing crawl_horizon_job...")
    call_command('crawl_horizon')

def generate_briefing_job():
    """
    Job to run the generate_daily_briefing command.
    """
    print("Executing generate_briefing_job...")
    call_command('generate_daily_briefing')

def crawl_bunker_prices_job():
    """
    Job to run the crawl_bunker_prices command.
    """
    print("Executing crawl_bunker_prices_job...")
    call_command('crawl_bunker_prices')

def cleanup_system_data_job():
    """
    Job to run the cleanup_system_data command.
    """
    print("Executing cleanup_system_data_job...")
    call_command('cleanup_system_data')

def backup_system_job():
    """
    Job to run the backup_system command.
    """
    print("Executing backup_system_job...")
    call_command('backup_system')

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no longer
    useful.
    
    :param max_age: The maximum age of job executions to keep, in seconds.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # 1. Add the crawl job (Daily at 02:00 AM)
        scheduler.add_job(
            crawl_news_job,
            trigger=CronTrigger(hour=2, minute=0),  # Run at 2:00 AM every day
            id="crawl_news_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'crawl_news_daily' to run at 02:00 daily."))

        # 2. Add the SOL crawl job (Daily at 03:00 AM)
        scheduler.add_job(
            crawl_sol_job,
            trigger=CronTrigger(hour=3, minute=0),  # Run at 3:00 AM every day
            id="crawl_sol_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'crawl_sol_daily' to run at 03:00 daily."))

        # 3. Add the ESHIP crawl job (Daily at 04:00 AM)
        scheduler.add_job(
            crawl_eship_job,
            trigger=CronTrigger(hour=4, minute=0),  # Run at 4:00 AM every day
            id="crawl_eship_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'crawl_eship_daily' to run at 04:00 daily."))

        # 4. Add the HORIZON crawl job (Daily at 05:00 AM)
        scheduler.add_job(
            crawl_horizon_job,
            trigger=CronTrigger(hour=5, minute=0),  # Run at 5:00 AM every day
            id="crawl_horizon_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'crawl_horizon_daily' to run at 05:00 daily."))

        # 5. Add the Daily Briefing job (Daily at 08:30 AM)
        scheduler.add_job(
            generate_briefing_job,
            trigger=CronTrigger(hour=8, minute=30),
            id="daily_briefing",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'daily_briefing' to run at 08:30 daily."))

        # 6. Add the Bunker Prices crawl job (Daily at 06:00 AM)
        scheduler.add_job(
            crawl_bunker_prices_job,
            trigger=CronTrigger(hour=6, minute=0),
            id="crawl_bunker_prices_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'crawl_bunker_prices_daily' to run at 06:00 daily."))

        # 7. Add System Data Cleanup job (Daily at 01:00 AM)
        scheduler.add_job(
            cleanup_system_data_job,
            trigger=CronTrigger(hour=1, minute=0),
            id="cleanup_system_data_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'cleanup_system_data_daily' to run at 01:00 daily."))

        # 8. Add System Backup job (Daily at 04:30 AM)
        scheduler.add_job(
            backup_system_job,
            trigger=CronTrigger(hour=4, minute=30),
            id="backup_system_daily",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'backup_system_daily' to run at 04:30 daily."))

        # 9. Add cleanup job (Weekly)
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS("Added job 'delete_old_job_executions'."))

        try:
            self.stdout.write(self.style.SUCCESS("Starting scheduler..."))
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Stopping scheduler..."))
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS("Scheduler shut down successfully!"))
