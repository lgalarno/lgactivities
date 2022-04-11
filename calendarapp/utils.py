# calendarapp/utils.py
# (c) Sajib Hossain sajib1066

from calendar import HTMLCalendar, monthrange
from django.shortcuts import reverse
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class Calendar(HTMLCalendar):
    def __init__(self, qs=None, d=None):  # year=None, month=None):
        self.qs = qs
        d = self.get_date(d)
        self.year = d.year
        self.month = d.month
        self.date_ = date(self.year, self.month, day=1)
        self.days_in_month = monthrange(self.year, self.month)[1]
        self.last = self.date_.replace(day=self.days_in_month)
        self.first = self.date_.replace(day=1)
        super(Calendar, self).__init__()

    def formatday(self, day, activities):
        """
        formats a day as a td
        filter activities by day

        :param day:
        :param activities:
        :return: list of activities for a the day in a table data (td) cell
        """
        activities_per_day = activities.filter(start_date_local__day=day)
        d = ''

        for activity in activities_per_day:
            # d += f'<li class="{activity.type}"> {activity.get_html_url} </li>'
            d += f'<li style="color: {activity.activity_type.color};"> {activity.get_html_url} </li>'

        if day != 0:
            return f"<td class='has_date'><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td  class='has_no_date' ></td>"

    def formatweek(self, theweek, activities):
        """
        formats a week as a tr

        :param theweek:
        :param activities:
        :return: a week in a table row (tr) of the calendar
        """
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, activities)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        """
        formats a month as a table
        filter activities by year and month
        :param withyear: write the year next to the month in the month row (tr) of the calendar
        :return: calendar
        """
        activities = self.qs.filter(start_date_local__year=self.year, start_date_local__month=self.month)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, activities)}\n'
        cal += '</table>\n'
        return cal

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        insert links to previous and next months in the calendar
        position is hardcoded according to the returned tr from
        the 'formatmonthname' method of the calendar/HTMLCalendar
        This may break in the future!
        """
        tr = super().formatmonthname(theyear, themonth, withyear=withyear)
        _link = reverse("calendarapp:calendar_view")
        next_month_link = f'&nbsp&nbsp<a class="links-arrow" href="{_link}?{self.next_month }"> > </a>'
        prev_month_link = f'<a class="links-arrow"  href="{_link}?{self.prev_month}"> < </a>&nbsp&nbsp'
        return tr[0:34] + prev_month_link + tr[34:-10] + next_month_link + tr[-10:]

    def get_date(self, req_day):
        if req_day:
            year, month = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
        else:
            latest_activity = self.qs.order_by('start_date').last()
            if latest_activity:
                return latest_activity.start_date
        return datetime.today()

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
