=====
Polls
=====

Polls is a Django application for creating and conducting web-based polls.

The application allows users to participate in polls and provides statistical
analysis of voting results through a REST API.

Features
--------

* creating and managing polls;
* voting;
* calculating the total number of votes;
* calculating votes for each answer;
* calculating percentage of votes;
* determining the most and least popular answers;
* filtering statistics by date;
* visualizing voting results;
* generating charts in SVG format.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'polls',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('polls/', include('polls.urls')),

3. Run ``python manage.py migrate`` to create the polls models.

4. Start the development server::

    python manage.py runserver

5. Visit http://127.0.0.1:8000/polls/ to use the application.