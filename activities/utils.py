# calendarapp/utils.py
# (c) Sajib Hossain sajib1066

from calendar import HTMLCalendar, monthrange

# from eventcalendar.helper import get_current_user
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta

from .models import Activity


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.date_ = date(self.year, self.month, day=1)
        self.days_in_month = monthrange(self.year, self.month)[1]
        self.last = self.date_.replace(day=self.days_in_month)
        self.first = self.date_.replace(day=1)
        super(Calendar, self).__init__()
    # formats a day as a td
    # filter activities by day
    def formatday(self, day, activities):
        activities_per_day = activities.filter(start_date_local__day=day)
        d = ''
        # TODO add color according to activity type in css
        for activity in activities_per_day:
            d += f'<li class="{activity.type}"> {activity.get_html_url} </li>'

        if day != 0:
            return f"<td class='has_date'><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td  class='has_no_date' ></td>"

    # formats a week as a tr
    def formatweek(self, theweek, activities):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, activities)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter activities by year and month
    def formatmonth(self, withyear=True):
        activities = Activity.objects.filter(start_date_local__year=self.year, start_date_local__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, activities)}\n'
        cal += '</table>\n'
        return cal

    @property
    def prev_year(self):
        prev_year = self.first + relativedelta(months=-12)  # timedelta(months=12)
        return 'month=' + str(prev_year.year) + '-' + str(prev_year.month)

    @property
    def next_year(self):
        next_year = self.last + relativedelta(months=+12)  # timedelta(months=12)
        return 'month=' + str(next_year.year) + '-' + str(next_year.month)

    @property
    def prev_month(self):
        prev_month = self.first - timedelta(days=1)
        return 'month=' + str(prev_month.year) + '-' + str(prev_month.month)

    @property
    def next_month(self):
        next_month = self.last + timedelta(days=1)
        return 'month=' + str(next_month.year) + '-' + str(next_month.month)


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


# def prev_year(d):
#     first = d.replace(day=1)
#     prev_year = first + relativedelta(months=-12)  # timedelta(months=12)
#     month = 'month=' + str(prev_year.year) + '-' + str(prev_year.month)
#     return month
#
#
# def next_year(d):
#     days_in_month = monthrange(d.year, d.month)[1]
#     last = d.replace(day=days_in_month)
#     next_year = last + relativedelta(months=+12)  # timedelta(months=12)
#     month = 'month=' + str(next_year.year) + '-' + str(next_year.month)
#     return month
#
#
# def prev_month(d):
#     first = d.replace(day=1)
#     prev_month = first - timedelta(days=1)
#     month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
#     return month
#
#
# def next_month(d):
#     days_in_month = monthrange(d.year, d.month)[1]
#     last = d.replace(day=days_in_month)
#     next_month = last + timedelta(days=1)
#     month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
#     return month
