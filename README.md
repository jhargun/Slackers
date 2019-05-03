# CSC630 Project 2: Slackers

Slackers is a basic direct messaging app that allows for the creation of users, creation of chats, and sending messages.

## Instructions
This app has already been uploaded to Heroku, and you can access it with the link provided in the project description. Operating it is relatively straightforward: there are forms and buttons for logging in, creating a user, editing user information, creating a chat, switching chats, and sending messages.

If you wish to run this app locally or reupload it somewhere else, you will simply need to `git clone` it:
```
git clone https://github.com/jhargun/Slackers
```

This app is built with the Django framework, so make sure that you have it with `pip install django` or by downloading it from [the website](https://www.djangoproject.com/).

Then, you will have to set up the Postgres server on your own. This can be done by running the following commands:

```
pip install postgres
pip install psycopg2-binary
pip install dj_database_url
```

Now, run the following command for macOS:
```
pg_ctl -D /usr/local/var/postgres start
```
Or the following for Windows:
```
pg_ctl -D /usr/local/var/postgres start
```

And continue:
```
createdb [database]
psql [database]
```

`[database]` here, as well as anything else in brackets, can be replaced with anything of your choosing.

Your prompt should now be database=#.

```
CREATE USER [user] WITH PASSWORD '[password]';
ALTER ROLE [user] SET client_encoding TO 'utf8';
ALTER ROLE [user] SET default_transaction_isolation TO 'read committed';
ALTER ROLE [user] SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE [database] TO [user];
\q
```

Now, we want to set the environment variable `DATABASE_URL`. For macOS, put this line in `~/.bashrc`:

```
export DATABASE_URL=postgres://[user]:[password]@localhost:5432/[database]
```

For Windows, you can set it through the GUI ("Edit the system environment variables").

And now, you should be done! Run `python manage.py migrate` to create the tables and `python manage.py runserver` to run the server!

For more information, refer to [these](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) [tutorials](https://devcenter.heroku.com/articles/heroku-postgresql).
