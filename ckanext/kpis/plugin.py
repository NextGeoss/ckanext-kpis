# -*- coding: utf-8 -*-
"""Contains the KPIs plugin and a modified tracking middleware plugin."""

from logging import getLogger
import sqlalchemy as sa
import hashlib
import urllib2

import ckan.plugins as p
import ckan.config.middleware.common_middleware as middleware
from ckan.common import config

from ckanext.kpis import helpers


log = getLogger(__name__)


class KPIsPlugin(p.SingletonPlugin):
    """The KPI plugin."""

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def after_map(self, map):
        """Add route for KPIs page."""
        map.connect('kpis', '/kpis',
                    controller='ckanext.kpis.controller:StatsController',
                    action='index')

        return map

    def update_config(self, config):
        """Update the CKAN config with KPI templates, resources, etc."""
        templates = 'templates'
        if p.toolkit.asbool(config.get('ckan.legacy_templates', False)):
                templates = 'templates_legacy'
        p.toolkit.add_template_directory(config, templates)
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('public/ckanext/kpis', 'ckanext-kpis')


class TrackingPlusMiddleware(object):
    """Replaces the core TrackingMiddleware, adding API tracking."""

    def __init__(self, app, config):
        """Use same procedure as CKAN core."""
        self.app = app
        self.engine = sa.create_engine(config.get('sqlalchemy.url'))

    def __call__(self, environ, start_response):
        """Track API calls as well as webpage hits."""
        path = environ['PATH_INFO']
        method = environ.get('REQUEST_METHOD')

        if (path == '/_tracking' and method == 'POST') \
            or (path.startswith('/api') and 'action' in path and
                '/api/3/action/status_show' not in path):

            # Get the URL and query for each case
            if path == '/_tracking' and method == 'POST':
                payload = environ['wsgi.input'].read()
                parts = payload.split('&')
                data = {}
                for part in parts:
                    k, v = part.split('=')
                    data[k] = urllib2.unquote(v).decode("utf8")
                url = data.get('url')
                tracking_type = data.get('type')
                start_response('200 OK', [('Content-Type', 'text/html')])
            elif path.startswith('/api') and 'action' in path:
                url = environ['PATH_INFO']
                tracking_type = 'api'

            # Do the tracking

            # We want a unique anonomized key for each user so that we do
            # not count multiple clicks from the same user.
            key = ''.join([
                environ['HTTP_USER_AGENT'],
                environ['REMOTE_ADDR'],
                environ.get('HTTP_ACCEPT_LANGUAGE', ''),
                environ.get('HTTP_ACCEPT_ENCODING', ''),
            ])
            key = hashlib.md5(key).hexdigest()

            # Store key/data here
            sql = '''INSERT INTO tracking_raw
                     (user_key, url, tracking_type)
                     VALUES (%s, %s, %s)'''
            self.engine.execute(sql, key, url, tracking_type)

            if tracking_type != 'api':
                return []

        return self.app(environ, start_response)


middleware.TrackingMiddleware = TrackingPlusMiddleware


show_graphs = p.toolkit.asbool(config.get('ckanext.kpis.show_graphs', False))
kpi_goals = helpers.get_goals()
