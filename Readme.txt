ONLINE TOPIC MODEL VISUALIZATION

Allison J. B. Chaney
achaney@princeton.edu

(C) Copyright 2011-2014, Allison J. B. Chaney

This is free software, you can redistribute it and/or modify it under
the terms of the GNU General Public License.

The GNU General Public License does not permit this software to be
redistributed in proprietary programs.

This software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

------------------------------------------------------------------------
DESCRIPTION

This code uses the Django web framework [https://www.djangoproject.com],
which will need to be installed. On Unix systems, this can be done with:

    sudo pip install Django

The BasicBrowser is an interface that lazily generates pages to display
the results of a topic model.  Since each page querys the database, the
browser can keep pace with online topic models, displaying current data.
It can also be used with topic models that are not online.

------------------------------------------------------------------------
INCLUDED FILES

* BasicBrowser: a directory containing an online topic model browser,
    written in Python using the Django framework.
    * static: directory containing javascript, css, image files
    * templates: directory containing template html files with Django 
        tags and filters
    * tmv_app: directory containing models and views files for the browser
        (see Django doc for more details)
    * db.py: a file to control writes to the database; this is generally 
        the file imported into external topic model source (see wiki example)
    * all other .py files that come standard with Django (see Django doc 
        for details)
* onlinewikipedia.py: a modified version of the Python script that comes
    with Online LDA (see below for source)
* Readme.txt: This file.
* COPYING: A copy of the GNU public license version 3.

------------------------------------------------------------------------
WIKIPEDIA DEMO

A demonstration of this browser can be run with the Wikipedia demo 
included with the Online LDA source:

    http://www.cs.princeton.edu/~blei/downloads/onlineldavb.tar

If you are not familiar with the Online LDA source, it is recommended that
you read its readme and explore its demo before proceeding.

To run the browser with the Wikipedia demo, substitute the original
[onlinewikipedia.py] file with provided replacement. For example:

    cp online-tmve/onlinewikipedia.py onlineldavb/onlinewikipedia.py

All paths to the database need to be absolute, so modify the following 
lines accordingly.

    onlinewikipedia.py, line 27
    BasicBrowser/settings.py, line 15

Finally, before running the demo, the database needs to be created.  In 
the BasicBrowser directory, run

    python manage.py syncdb

At this point the Online LDA demo can be run as specified in its readme, e.g.

    python onlinewikipedia.py 101

to run the algorithms for 101 iterations (which isn't very long).

To view the browser, run the following in the BasicBrowser directory:

    python manage.py runserver

and navigate to the following link in a web browser, reloading as desired.
(The topics make take a while to be created and populated with terms.)

    http://127.0.0.1:8000/topic_presence

Viewing a given page of the browser make take longer while the topic model
is running than it does after the run completes.

If you want to start over again, remove the database file, sync the database
again before restarting the model.

    rm tmv_db; python manage.py syncdb

To install the browser on a web server, see the Django documentation.

------------------------------------------------------------------------
USING THE BROWSER WITH OTHER TOPIC MODELS

The browser can be used for any topic model, even if the model is not online.
For algorithms written in Python, simply import the db.py file and use its
functions to write to the database.  For algorithms not written in Python, 
you need only write your data to the database, which can be done directly 
with sqlite3, by embeding the db.py file in your code, or by using any other
method that works for you.  If you have the output of a model in a file, it
might be easiest to write a python script to transfer that data using db.py.
It shoudl be noted that as written, db.py uses a separate thread for most 
writes to the database; this may not be ideal for all applications.
