# encoding: utf-8

import datetime
import calendar
from sqlalchemy import Table, select, join, func, and_, distinct

from ckan.common import config
import ckan.plugins as p
import ckan.model as model

from ckanext.kpis.plugin import kpi_goals


DATE_FORMAT = '%Y-%m-%d'

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

def datetime2date(datetime_):
    if type(datetime_) == int:
        datetime_ = datetime.datetime.utcnow()
    return datetime.date(datetime_.year, datetime_.month, datetime_.day)

def get_first_date():
    """Return the starting date for calculating all the KPIs.
    If the date isn't specified in the config, then the earliest revision
    date is used instead.

    The format of the date in the config must be `YYYY/mm/dd`.
    """
    config_date = config.get('ckanext.kpis.first_date')
    if not config_date:
        revision = table('revision')
        s = select([func.min(revision.c.timestamp)],\
            from_obj=[revision])
        first_date = model.Session.execute(s).fetchone()[0].date()
    else:
        first_date = datetime.datetime.strptime(config_date, '%Y/%m/%d').date()
    return first_date

first_date = get_first_date()


def calc_percentage(goal, value):
    """Return the percentage of the goal completed."""
    return round(100 * (float(value) / float(goal)), 2)

def get_days_in_month(day):
    """Return the number days in the month that the day is part of."""
    return calendar.monthrange(day.year, day.month)[1]


class UsageStats(object):

    @classmethod
    def get_weeks(cls):
        today = datetime.datetime.utcnow().date()
        week_start = first_date - datetime.timedelta(days=datetime.date.weekday(first_date))
        weeks = []
        while week_start <= today:
            week_end = week_start + datetime.timedelta(days=6)
            weeks.append((week_start, week_end))
            week_start = week_end + datetime.timedelta(days=1)
        return weeks

    @classmethod
    def get_months(cls):
        today = datetime.datetime.utcnow().date()
        end_of_last_month = today.replace(day=1) - datetime.timedelta(days=1)
        month_start = first_date.replace(day=1)
        months = []
        while month_start < end_of_last_month:
            days = get_days_in_month(month_start)
            month_end = month_start + datetime.timedelta(days=days-1)
            months.append((month_start, month_end))
            month_start = month_end + datetime.timedelta(days=1)
        return months

    @classmethod
    def get_monthly_user_counts(cls, tracking_type):
        months = cls.get_months()
        visits_for_months = cls.get_visit_counts_for_months(tracking_type, months)
        return visits_for_months

    @classmethod
    def get_dataset_counts(cls, set_type):
        weeks = cls.get_weeks()
        counts = cls.get_dataset_counts_for_weeks(set_type, weeks)
        return counts

    @classmethod
    def get_visit_counts_for_months(cls, tracking_type, months):
        visit_counts_for_months = []
        for month in months:
            count = cls.get_visits_for_month(tracking_type, month)
            percent = calc_percentage(kpi_goals['monthly_users'], count)
            visit_counts_for_months.append((month[0].strftime(DATE_FORMAT),
                count, percent))
        return visit_counts_for_months

    @classmethod
    def get_dataset_counts_for_weeks(cls, set_type, weeks):
        """Returns a list of the total number of datasets or harvesters,
        depending on the set_type, plus the completion percentage for
        the respective KPI goal for each week in weeks.
        """
        dataset_counts_for_weeks = []
        count = 0
        # Determine the correct goal
        if set_type == 'dataset':
            goal = kpi_goals['total_datasets']
        elif set_type == 'harvest':
            goal = kpi_goals['total_sources']
        for week in weeks:
            count += cls.get_datasets_for_week(set_type, week)
            percent = calc_percentage(goal, count)
            dataset_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count, percent))
        return dataset_counts_for_weeks

    @classmethod
    def get_datasets_for_week(cls, set_type, week):
        package = table('package')
        package_revision = table('package_revision')
        revision = table('revision')
        s = select([func.count(package.c.id)], from_obj=[package]).\
            where(and_(package.c.type==set_type,
                package.c.metadata_created >= week[0],
                package.c.metadata_created <= week[1]))
        new_sets = model.Session.execute(s).fetchone()[0]
        s = select([func.count(package_revision.c.id)], from_obj=[package_revision.join(revision)]).\
            where(and_(package_revision.c.type==set_type,
                package_revision.c.state==model.State.DELETED,
                revision.c.timestamp >= week[0], revision.c.timestamp <= week[1]))
        deleted_sets = model.Session.execute(s).fetchone()[0]
        count_for_week = new_sets - deleted_sets
        return count_for_week

    @classmethod
    def get_visits_for_month(cls, tracking_type, month):
        """Get the number of unique users for a given month."""
        tracking_raw = table('tracking_raw')
        if tracking_type == 'all':
            tracking_query = and_(tracking_raw.c.access_timestamp >= month[0],\
                tracking_raw.c.access_timestamp <= month[1])
        else:
            tracking_query = and_(tracking_raw.c.tracking_type == tracking_type,\
                tracking_raw.c.access_timestamp >= month[0],\
                tracking_raw.c.access_timestamp <= month[1])
        s = select([func.count(distinct(tracking_raw.c.user_key))],\
            from_obj=[tracking_raw]).\
            where(tracking_query)
        count_for_month = model.Session.execute(s).fetchone()[0]
        return count_for_month
