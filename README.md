# Flask-jwt-swagger
## Flask app using jwt and swagger API documentation

This repository contains a simple flask app with jwt authentication implemented on an endpoint, as well as the swagger API documentation on a sample endpoint


*http://127.0.0.1:4444/*
> main page with a simple login form that checks whether the credentials are present in the db

*http://127.0.0.1:4444/register*
> account registration page that inserts credentials into the db. Duplicate usernames are handled

*http://127.0.0.1:4444/login*
> page for jwt authentication. Username and Password is checking against db, and a token is provided on successful authentication

*http://127.0.0.1:4444/todo?token=[inserttokenhere]*
> api endpoint containing the `token_required` decorator, forcing it to only be accessed if the jwt token is provided.

*http://127.0.0.1:4444/docs*
> Swagger API documentation for an endpoint with dummy data


## Usage Notes
* Create a virtual enviroment with python==3.6.9.
* Install dependencies with `pip install -r requirements.txt`
* config file "db.yaml" and mysql db file not present in the repository


