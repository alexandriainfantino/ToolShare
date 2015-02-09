ToolShare
======

Installation Instructions
------

1. Install python3.

2. Install django 1.6 and pysqlite
      pip3 install django==1.6
      pip3 install pysqlite

3. In SWEN/settings.py, set credentials for SMTP server for outgoing email.
   It's currently set up to send an email via a Gmail account, so fill in
   the settings with your email username and password.

   For testing it's recommended that EMAIL_ACTUALLY_SEND be set to False so that
   you don't risk being caught in spam filters. The emails will be logged to the
   console.

4. Sync database. Note: When it prompts you to create a superuser, respond 'no'.
      python3 manage.py syncdb

5. Run server (see below), navigate to the website and submit initial
   registration form. This will initialize the website and create a shed.


Running Instructions
------

To run the server on port 80, run the following command:
      python3 runserver 0.0.0.0:80

