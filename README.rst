.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/NextGeoss/ckanext-kpis.svg?branch=master
    :target: https://travis-ci.org/nextgeoss/ckanext-kpis

.. image:: https://coveralls.io/repos/nextgeoss/ckanext-kpis/badge.svg
  :target: https://coveralls.io/r/nextgeoss/ckanext-kpis


=============
ckanext-kpis
=============

ckanext-kpis tracks and presents KPIs on a dedicated page.

Goals can be defined in the portal configuration file.

The goals/tracking currently supported are:

1. Number of datasets, evaluated weekly

2. Number of sources/harvesters, evaluated weekly

3. Number of unique monthly users (of the website and of the API)

The extension is based on ckanext-stats, though most of the back end
code is different now. The basic presentation on the front end remains
much the same.

The extension replaces the CKAN core TrackingMiddleware with a modified
version that also tracks API calls.


------------
Requirements
------------

ckanext-kpis works with CKAN version 2.6.x and up. There are no additional requirements.


------------
Installation
------------

To install ckanext-kpis, activate your CKAN virtualenv and
do:

    git clone https://github.com/nextgeoss/ckanext-kpis.git
    cd ckanext-kpis
    python setup.py develop


---------------
Config Settings
---------------

    # Set the start date for displaying stats on the portal
    # (not the date on which tracking begins, but the earliest
    # date for which you want to display stats).
    # (Optional. Default value: the date of the first revision
    # in the CKAN database)
    # Format: YYYY/mm/dd
    ckanext.kpis.first_date = 2017/04/19

    # By default, the KPI stats are displayed in a table. If this
    # setting is enabled, a graph of the stats will also be 
    # displayed above each table.
    # (Optional. Default value: False)
    ckanext-kpis.show_graphs = True

    # The goals for the total number of datasets, total number of
    # harvesters/sources and the number of monthly users can be
    # configured with a JSON dictionary.
    # (Optional. Default values: see exmple below)
    # Format: {"total_datasets": an_integer, "monthly_users": an_integer, "total_sources": an_integer}
    ckanext.kpis.goals={"total_datasets": 10000000, "monthly_users": 2000, "total_sources": 10}
