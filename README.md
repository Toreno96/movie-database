# Movie Database

Simple REST API - a basic movie database interacting with external API.


## Full specification of endpoints

Single check mark (✓) means the feature is implemented.  
Double check mark (✓✓) means the feature _and_ its automated tests are implemented.

1. POST /movies:
    - Request body should contain only movie title ✓✓, and its presence should be validated ✓✓.
    - Based on passed title ✓✓, other movie details should be fetched from <http://www.omdbapi.com/> ✓✓ (or other similar, public movie database) - and saved to application database ✓✓.
    - Request response should include full movie object ✓✓, along with all data fetched from external API ✓✓.

2. GET /movies:
    - Should fetch list of all movies already present in application database ✓✓.
    - (optional) Additional filtering (by ID ✓✓), sorting.

3. POST /comments:
    - Request body should contain ID of movie ✓✓ already present in database ✓✓, and comment text body ✓✓.
    - Comment should be saved to application database ✓✓ and returned in request response ✓✓.

4. GET /comments:
    - Should fetch list of all comments present in application database ✓✓.
    - Should allow filtering comments by associated movie, by passing its ID ✓✓.

5. GET /top:
    - Should return top movies already present in the database ✓✓ ranking based on a number of comments added to the movie (as in the example) ✓✓ in the specified date range ✓✓. The response should include the ID of the movie ✓✓, position in rank ✓✓ and total number of comments (in the specified date range) ✓✓.
    - Movies with the same number of comments should have the same position in the ranking ✓✓.
    - Should require specifying a date range for which statistics should be generated ✓✓.


## Example response

```
[

    {

        "movie_id": 2,

        "total_comments": 4,

        "rank": 1

    },

    {

        "movie_id": 3,

        "total_comments": 2,

        "rank": 2

    },

    {

        "movie_id": 4,

        "total_comments": 2,

        "rank": 2

    },

    {

        "movie_id": 1,

        "total_comments": 0,

        "rank": 3

    }

]
```


## Installation

### Clone this repository

```
$ https://github.com/Toreno96/movie-database.git
$ cd movie-database
```

### Setup Python virtualenv

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

### Environment variables

#### Required

- `SECRET_KEY` - secret key used by Django.
- `OMDB_API_KEY` - API key to OMDb API.
- `DEBUG` - any boolean value supported by Python function [`distutils.util.strtobool`](https://docs.python.org/3/distutils/apiref.html?highlight=strtobool#distutils.util.strtobool); if true, sets application in debug mode.

#### Optional

- `POSTGRES_NAME` - defaults to `moviedatabase`.
- `POSTGRES_USER` - defaults to `moviedatabase`.
- `POSTGRES_HOST` - defaults to `127.0.0.1`.
- `POSTGRES_PORT` - defaults to `5432`.

### Prepare the database

[Install and configure](https://wiki.archlinux.org/index.php/PostgreSQL) PostgreSQL database.

**Remember that database user must be a superuser**.

If configuration differs from defaults, above-mentioned optional environment variables becomes required.

Finally, migrate the database:
```
$ python manage.py migrate
```

### Run server

```
$ python manage.py runserver
```

You should see similar output to:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 25, 2019 - 20:20:04
Django version 2.2.2, using settings 'moviedatabase.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```


## Tests

To run automated tests, use:
```
$ python manage.py test moviedatabase.moviedatabase
```

Alternatively:
```
$ coverage run --source='moviedatabase.moviedatabase' manage.py test moviedatabase.moviedatabase
```

And see coverage report:
```
$ coverage report -m
```
