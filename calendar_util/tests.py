from django.test import TestCase
import datetime
from calendar_util.models import Holidays, Holiday
from calendar_util.constants import *
from django.contrib.auth.models import User
from calendar_util.util import *
import calendar as cal

class HolidayTests(TestCase):
    def setUp(self):
        self.the_date = Holiday.objects.create(date=THE_DATE.date(),
                                               description="The Date",
                                               creator=User.objects.get(username="kuhlc0"))
        self.the_date.save()
        self.the_other_date = Holiday.objects.create(date=THE_DATE.date().replace(year=2099),
                                               description="The Date",
                                               creator=User.objects.get(username="kuhlc0"))
        self.the_other_date.save()
    def tearDown(self):
        self.the_date.delete()
        Holidays().refresh()
    def test_christmas(self):
        christmas = datetime.date(2018, 12, 25)
        self.assertTrue(christmas in Holidays())
    def test_new_holiday(self):
        for h in Holiday.objects.all():
            print(h.date, h.description)
        for h in Holidays().holidays:
            print(h)
        print(self.the_other_date.date)
        self.assertFalse(THE_DATE.date() in Holidays())
        self.assertTrue(self.the_other_date.date in Holidays())
    def test_create_holiday(self):
        test_date = THE_DATE.date().replace(year=2041)
        the_date = Holiday.objects.create(date=test_date,
                                          description="The Test Date",
                                          creator=User.objects.get(username="kuhlc0"))
        the_date.save()
        the_date = Holiday.objects.get(date=test_date)
        self.assertIsNotNone(the_date)
        Holidays().refresh()
        self.assertTrue(test_date in Holidays())

class UtilTests(TestCase):
    def setUp(self):
        cal.setfirstweekday(cal.MONDAY)
    def test_next_friday(self):
        test_friday = datetime.date(2010, 3, 5)
        self.assertEqual(test_friday, next_friday(THE_DATE).date())
        test_friday = next_friday()
        self.assertEqual(cal.weekday(test_friday.year, test_friday.month, test_friday.day), 4)
    def test_last_monday(self):
        test_monday = datetime.date(2010, 3, 1)
        self.assertEqual(test_monday, last_monday(THE_DATE).date())
        test_monday = last_monday()
        self.assertEqual(cal.weekday(test_monday.year, test_monday.month, test_monday.day), 0)
    def test_workday(self):
        self.assertEqual(next_workday(THE_DATE).date(), datetime.date(2010,3,2))
        self.assertTrue(is_workday(THE_DATE))
        self.assertEqual(to_workday(THE_DATE), THE_DATE)
        self.assertEqual(workday_offset(THE_DATE, -1).date(), datetime.date(2010,2,26))
        self.assertEqual(workday_offset(THE_DATE, 1).date(), datetime.date(2010,3,2))
        self.assertEqual(workday_offset(THE_DATE, -2).date(), datetime.date(2010,2,25))
    def test_ultimo(self):
        self.assertEqual(next_ultimo(DAILY, THE_DATE).date(), datetime.date(2010,3,2))
        self.assertEqual(next_ultimo(MONTHLY, THE_DATE).date(), datetime.date(2010,3,31))
        self.assertEqual(next_ultimo(QUARTERLY, THE_DATE).date(), datetime.date(2010,3,31))
        self.assertEqual(next_ultimo(YEARLY, THE_DATE).date(), datetime.date(2010,12,31))
    def test_specstr(self):
        self.assertEqual(specstr(DAILY, THE_DATE), "01.03.")
        self.assertEqual(specstr(MONTHLY, THE_DATE), "Mar")
        self.assertEqual(specstr(QUARTERLY, THE_DATE), "Q1")
        self.assertEqual(specstr(YEARLY, THE_DATE), "2010")
    def test_shift_date(self):
        shift_day = shift_date(THE_DATE, 6)
        shift_month = shift_date(THE_DATE, 6, MONTHLY)
        shift_year = shift_date(THE_DATE, 6, YEARLY)
        self.assertEqual(shift_day.date(), datetime.date(2010,3,7))
        self.assertEqual(shift_month.date(), datetime.date(2010,9,1))
        self.assertEqual(shift_year.date(), datetime.date(2016,3,1))
