import datetime
import pytz
from django.conf import settings

def calculate_parking_cost(start_date, end_date):
    busy_seconds, standard_seconds, weekend_seconds = datetime.timedelta(), datetime.timedelta(), datetime.timedelta()

    price_list = settings.PRICE_LIST

    last_breakpoint = start_date
    timezone = pytz.timezone(settings.TIME_ZONE)

    def append_tariff(breakpoint, end_date=end_date):

        nonlocal timezone
        nonlocal last_breakpoint
        second = datetime.timedelta(seconds=1)
        breakpoint = timezone.localize(breakpoint)

        if breakpoint > end_date:
            add_time = end_date - last_breakpoint + second
            last_breakpoint = end_date
        else:
            add_time = breakpoint - last_breakpoint + second
            last_breakpoint = breakpoint + second

        return add_time

    while last_breakpoint < end_date:

        if last_breakpoint.weekday() < 5:

            if last_breakpoint.hour in price_list['busy']['hours'][0]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               9, 59, 59)
                busy_seconds += append_tariff(breakpoint)

            elif last_breakpoint.hour in price_list['busy']['hours'][1]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               17, 59, 59)
                busy_seconds += append_tariff(breakpoint)

            elif last_breakpoint.hour in price_list['standard']['hours'][0]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               6, 59, 59)
                standard_seconds += append_tariff(breakpoint)

            elif last_breakpoint.hour in price_list['standard']['hours'][1]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               14, 59, 59)
                standard_seconds += append_tariff(breakpoint)

            elif last_breakpoint.hour in price_list['standard']['hours'][2]:

                breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month, last_breakpoint.day,
                                               23, 59, 59)
                standard_seconds += append_tariff(breakpoint)
        else:
            breakpoint = datetime.datetime(last_breakpoint.year, last_breakpoint.month,
                                           last_breakpoint.day, 23, 59, 59)
            weekend_seconds += append_tariff(breakpoint)

    return (busy_seconds / 3600 * price_list['busy']['price']).seconds \
           + (standard_seconds / 3600 * price_list['standard']['price']).seconds \
           + (weekend_seconds / 3600 * price_list['weekend']['price']).seconds