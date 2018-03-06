import pytz
import datetime

TIMEZONE_DJANGO = "Europe/Berlin"
TIMEZONE = pytz.timezone(TIMEZONE_DJANGO)
DATE_FORMAT_DJANGO = "d.m.Y"
DATETIME_FORMAT_DJANGO = DATE_FORMAT_DJANGO + " H:i"
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = DATE_FORMAT + " %H:%M"

DAILY = 'DLY'
MONTHLY = 'MTH'
QUARTERLY = 'QTR'
YEARLY = 'YLY'

DATETIME_INPUT_FORMATS = [
    '%d.%m.%Y %H:%M',        # '25.10.2006 14:30'
    '%d.%m.%Y %H:%M:%S',     # '25.10.2006 14:30:59'
    '%d.%m.%Y',              # '25.10.2006'
    '%d%m%y',                # '251006'
    '%d%m%Y',                # '25102006'
    '%Y%m%d %H:%M',          # '20061025 14:30'
    '%Y%m%d %H:%M:%S',       # '20061025 14:30:59'
    '%Y%m%d',                # '20061025'
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y'               # '10/25/06'
]

DATE_INPUT_FORMATS = [fstr.split()[0] for fstr in DATETIME_INPUT_FORMATS]

THE_DATE = datetime.datetime(year=2010, month=3, day=1, hour=2, minute=4, tzinfo=TIMEZONE)
