from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.core.kite import kite

from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.core.auto_login import (
    auto_generate_access_token
)


scheduler = BackgroundScheduler()


def refresh_kite_token():

    try:

        token = auto_generate_access_token()
        
        kite.set_access_token(token)

        print(
            "Access token refreshed successfully"
        )

        print(token)

    except Exception as e:

        print(
            f"Token refresh failed: {e}"
        )


def start_scheduler():

    scheduler.add_job(

        refresh_kite_token,

        CronTrigger(
            hour=8,
            minute=55,
            timezone=ZoneInfo("Asia/Kolkata")   
        ),

        id="kite_token_refresh",

        replace_existing=True
    )

    scheduler.start()

    print(
        "Scheduler started"
    )