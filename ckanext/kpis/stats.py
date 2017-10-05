# encoding: utf-8

import datetime
from sqlalchemy import Table, select, join, func, and_, distinct

from ckan.common import config
import ckan.plugins as p
import ckan.model as model


DATE_FORMAT = '%Y-%m-%d'

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

def datetime2date(datetime_):
    if type(datetime_) == int:
        datetime_ = datetime.datetime.utcnow()
    return datetime.date(datetime_.year, datetime_.month, datetime_.day)

def get_first_date():
    first_date = config.get('ckanext.kpis.first_date')
    if not first_date:
        tracking_raw = table('tracking_raw')
        s = select([func.min(tracking_raw.c.access_timestamp)],\
            from_obj=[tracking_raw])
        first_date = model.Session.execute(s).fetchone()[0].date()
    else:
        first_date = datetime.datetime.strptime('01/Jun/2017', '%d/%b/%Y').date()
    return first_date

first_date = get_first_date()


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
    def get_days(cls, week):
        days = []
        day_one = week[0]
        days.append(day_one)
        for i in range(1,6):
            days.append(day_one + datetime.timedelta(days=i))
        days.append(week[1])
        return days

    @classmethod
    def get_hit_counts(cls, tracking_type):
        weeks = cls.get_weeks()
        hit_counts_for_weeks = cls.get_hit_counts_for_weeks(tracking_type, weeks)
        return hit_counts_for_weeks

    @classmethod
    def get_visit_counts(cls, tracking_type):
        weeks = cls.get_weeks()
        visit_counts_for_weeks = cls.get_visit_counts_for_weeks(tracking_type, weeks)
        return visit_counts_for_weeks

    @classmethod
    def get_dataset_counts(cls, set_type):
        weeks = cls.get_weeks()
        counts = cls.get_dataset_counts_for_weeks(set_type, weeks)
        return counts


    @classmethod
    def get_resource_counts(cls):
        weeks = cls.get_weeks()
        counts = cls.get_resource_counts_for_weeks(weeks)
        return counts


    @classmethod
    def get_organization_counts(cls):
        weeks = cls.get_weeks()
        counts = cls.get_organization_counts_for_weeks(weeks)
        return counts


    @classmethod
    def get_hit_counts_for_weeks(cls, tracking_type, weeks):
        hit_counts_for_weeks = []
        for week in weeks:
            count = cls.get_hits_for_week(tracking_type, week)
            hit_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count))
        return hit_counts_for_weeks

    @classmethod
    def get_visit_counts_for_weeks(cls, tracking_type, weeks):
        visit_counts_for_weeks = []
        for week in weeks:
            count = cls.get_visits_for_week(tracking_type, week)
            visit_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count))
        return visit_counts_for_weeks


    @classmethod
    def get_dataset_counts_for_weeks(cls, set_type, weeks):
        dataset_counts_for_weeks = []
        count = 0
        for week in weeks:
            count += cls.get_datasets_for_week(set_type, week)
            dataset_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count))
        return dataset_counts_for_weeks

    @classmethod
    def get_resource_counts_for_weeks(cls, weeks):
        dataset_counts_for_weeks = []
        count = 0
        for week in weeks:
            count += cls.get_resources_for_week(week)
            dataset_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count))
        return dataset_counts_for_weeks


    @classmethod
    def get_organization_counts_for_weeks(cls, weeks):
        dataset_counts_for_weeks = []
        count = 0
        for week in weeks:
            count += cls.get_organizations_for_week(week)
            dataset_counts_for_weeks.append((week[0].strftime(DATE_FORMAT),
                count))
        return dataset_counts_for_weeks


    @classmethod
    def get_hits_for_week(cls, tracking_type, week):
        tracking_raw = table('tracking_raw')
        s = select([func.count(tracking_raw.c.access_timestamp)], from_obj=[tracking_raw]).\
            where(and_(tracking_raw.c.tracking_type == tracking_type, tracking_raw.c.access_timestamp >= week[0], tracking_raw.c.access_timestamp <= week[1]))
        count_for_week = model.Session.execute(s).fetchone()[0]
        return count_for_week


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
    def get_resources_for_week(cls, week):
        resource = table('resource')
        resource_revision = table('resource_revision')
        revision = table('revision')
        s = select([func.count(resource.c.id)], from_obj=[resource]).\
            where(and_(resource.c.created >= week[0],
                resource.c.created <= week[1]))
        new_resources = model.Session.execute(s).fetchone()[0]
        s = select([func.count(resource_revision.c.id)], from_obj=[resource_revision.join(revision)]).\
            where(and_(resource_revision.c.state==model.State.DELETED,
                revision.c.timestamp >= week[0], revision.c.timestamp <= week[1]))
        deleted_resources = model.Session.execute(s).fetchone()[0]
        count_for_week = new_resources - deleted_resources
        return count_for_week


    @classmethod
    def get_organizations_for_week(cls, week):
        organization = table('group')
        organization_revision = table('group_revision')
        revision = table('revision')
        s = select([func.count(organization.c.id)], from_obj=[organization]).\
            where(and_(organization.c.created >= week[0],
                organization.c.created <= week[1]))
        new_organizations = model.Session.execute(s).fetchone()[0]
        s = select([func.count(organization_revision.c.id)], from_obj=[organization_revision.join(revision)]).\
            where(and_(organization_revision.c.type=='organization',
                organization_revision.c.state==model.State.DELETED,
                revision.c.timestamp >= week[0], revision.c.timestamp <= week[1]))
        deleted_organizations = model.Session.execute(s).fetchone()[0]
        count_for_week = new_organizations - deleted_organizations
        return count_for_week


    @classmethod
    def get_visits_for_day(cls, tracking_type, day):
        tracking_raw = table('tracking_raw')
        day_two = day + datetime.timedelta(days=1)
        s = select([func.count(distinct(tracking_raw.c.user_key))],\
            from_obj=[tracking_raw]).\
            where(and_(tracking_raw.c.tracking_type == tracking_type,\
            tracking_raw.c.access_timestamp >= day,\
            tracking_raw.c.access_timestamp < day_two))
        count_for_day = model.Session.execute(s).fetchone()[0]
        return count_for_day

    @classmethod
    def get_visits_for_week(cls, tracking_type, week):
        days = cls.get_days(week)
        visits_for_week = 0
        for day in days:
            visits = cls.get_visits_for_day(tracking_type, day)
            visits_for_week += visits
        return visits_for_week
