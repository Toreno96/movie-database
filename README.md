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
    - Should return top movies already present in the database ranking based on a number of comments added to the movie (as in the example) in the specified date range. The response should include the ID of the movie, position in rank and total number of comments (in the specified date range).
    - Movies with the same number of comments should have the same position in the ranking.
    - Should require specifying a date range for which statistics should be generated.


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
