from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.core.kite import kite
import logging

from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.core.auto_login import (
    auto_generate_access_token
)


logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def refresh_kite_token():

    try:

        token = auto_generate_access_token()
        
        kite.set_access_token(token)

        logger.info(
            "Access token refreshed successfully"
        )

        logger.info(token)
        
        return True

    except Exception as e:

        logger.exception(
            f"Token refresh failed: {e}"
        )
        
        return False


def start_scheduler():

    scheduler.add_job(

        refresh_kite_token,

        CronTrigger(
            hour="4,8,12,16,20,24",
            minute=55,
            timezone=ZoneInfo("Asia/Kolkata")   
        ),

        id="kite_token_refresh",

        replace_existing=True
    )

    scheduler.start()

    logger.info(
        "Scheduler started"
    )