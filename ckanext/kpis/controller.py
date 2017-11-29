# encoding: utf-8
"""Contains the controller for KPI page."""

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
    """Controller for KPI pages."""

    def index(self):
        """Render the KPI index page."""
        c = p.toolkit.c

        c.show_graphs = show_graphs
        c.kpi_goals = kpi_goals

        usage_stats = stats_lib.UsageStats()

        monthly_users = usage_stats.get_monthly_user_counts('all')
        c.num_users_by_month = [
            {
                'date': h.date_str_to_datetime(month_date),
                'users': users,
                'percent_complete': percentage
            }
            for month_date, users, percentage in monthly_users
        ]
        if not c.num_users_by_month:
            c.num_users_by_month = [
                {
                    'date': DUMMY_DATE,
                    'users': 0,
                    'percent_complete': 0
                }
            ]

        weekly_datasets = usage_stats.get_dataset_counts('dataset')
        c.raw_packages_by_week = [
            {
                'date': h.date_str_to_datetime(week_date),
                'total_packages': cumulative_num_hits,
                'percent_complete': percentage
            }
            for week_date, cumulative_num_hits, percentage in weekly_datasets
        ]
        if not c.raw_packages_by_week:
            c.raw_packages_by_week = [
                {
                    'date': DUMMY_DATE,
                    'total_packages': 0,
                    'percent_complete': 0
                }
            ]

        weekly_harvesters = usage_stats.get_dataset_counts('harvest')
        c.raw_harvesters_by_week = [
            {
                'date': h.date_str_to_datetime(week_date),
                'total_packages': sources,
                'percent_complete': percentage
            }
            for week_date, sources, percentage in weekly_harvesters
        ]
        if not c.raw_harvesters_by_week:
            c.raw_harvesters_by_week = [
                {
                    'date': DUMMY_DATE,
                    'total_packages': 0,
                    'percent_complete': 0
                }
            ]

        return p.toolkit.render('ckanext/kpis/index.html')
