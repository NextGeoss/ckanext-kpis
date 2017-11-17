# encoding: utf-8

import ckan.plugins as p
from ckan.lib.base import BaseController
import stats as stats_lib
import ckan.lib.helpers as h

from ckanext.kpis.plugin import show_graphs
from ckanext.kpis.plugin import kpi_goals
from ckanext.kpis.stats import first_date
from ckanext.kpis.stats import DATE_FORMAT

DUMMY_DATE = h.date_str_to_datetime(first_date.strftime(DATE_FORMAT))

class StatsController(BaseController):

    def index(self):
        c = p.toolkit.c

        c.show_graphs = show_graphs
        c.kpi_goals = kpi_goals

        usage_stats = stats_lib.UsageStats()
        c.num_api_calls_by_week = usage_stats.get_hit_counts('api')
        c.num_hits_by_week = usage_stats.get_hit_counts('page')
        c.num_api_visits_by_week = usage_stats.get_visit_counts('api')
        c.num_page_visits_by_week = usage_stats.get_visit_counts('page')
        c.num_datasets_by_week = usage_stats.get_dataset_counts('dataset')
        c.num_harvesters_by_week = usage_stats.get_dataset_counts('harvest')
        c.num_resources_by_week = usage_stats.get_resource_counts()
        c.num_organizations_by_week = usage_stats.get_organization_counts()


        c.num_users_by_month = [{'date': h.date_str_to_datetime(month_date),\
            'users': users, 'percent_complete': percentage} for month_date,\
            users, percentage in usage_stats.get_monthly_user_counts('all')]
        if not c.num_users_by_month:
            c.num_users_by_month = [{'date': DUMMY_DATE, 'users': 0, 'percent_complete': 0}]


        c.raw_packages_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_packages': cumulative_num_hits, \
            'percent_complete': percentage} for week_date,\
            cumulative_num_hits, percentage in c.num_datasets_by_week]
        if not c.raw_packages_by_week:
            c.raw_packages_by_week = [{'date': DUMMY_DATE, 'total_packages': 0, 'percent_complete': 0}]

        c.raw_resources_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_resources': cumulative_num_hits} for week_date,\
            cumulative_num_hits in c.num_resources_by_week]
        if not c.raw_resources_by_week:
            c.raw_resources_by_week = [{'date': DUMMY_DATE, 'total_resources': 0}]

        c.raw_organizations_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_organizations': cumulative_num_hits} for week_date,\
            cumulative_num_hits in c.num_organizations_by_week]
        if not c.raw_organizations_by_week:
            c.raw_organizations_by_week = [{'date': DUMMY_DATE, 'total_organizations': 0}]

        c.raw_harvesters_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_packages': sources, \
            'percent_complete': percentage} for week_date,\
            sources, percentage in c.num_harvesters_by_week]
        if not c.raw_harvesters_by_week:
            c.raw_harvesters_by_week = [{'date': DUMMY_DATE, 'total_packages': 0, 'percent_complete': 0}]

        c.raw_api_calls_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_hits': cumulative_num_hits} for week_date,\
            cumulative_num_hits in c.num_api_calls_by_week]
        if not c.raw_api_calls_by_week:
            c.raw_api_calls_by_week = [{'date': DUMMY_DATE, 'total_hits': 0}]

        c.raw_hits_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_hits': cumulative_num_hits} for week_date,\
            cumulative_num_hits in c.num_hits_by_week]
        if not c.raw_hits_by_week:
            c.raw_hits_by_week = [{'date': DUMMY_DATE, 'total_hits': 0}]

        c.raw_api_visits_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_visits': cumulative_num_visits} for week_date,\
            cumulative_num_visits in c.num_api_visits_by_week]
        if not c.raw_api_visits_by_week:
            c.raw_api_visits_by_week = [{'date': DUMMY_DATE, 'total_visits': 0}]

        c.raw_page_visits_by_week = [{'date': h.date_str_to_datetime(week_date),\
            'total_visits': cumulative_num_visits} for week_date,\
            cumulative_num_visits in c.num_page_visits_by_week]
        if not c.raw_page_visits_by_week:
            c.raw_page_visits_by_week = [{'date': DUMMY_DATE, 'total_visits': 0}]

        return p.toolkit.render('ckanext/kpis/index.html')
