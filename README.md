# Dash tempate for SNAP tools

## Local development

After cloning this template, run it this way:

```
pipenv install
export FLASK_APP=application.py
export FLASK_DEBUG=1
pipenv run flask run
```

The project is run through Flask and will be available at [http://localhost:5000](http://localhost:5000).

## Deploying to AWS Elastic Beanstalk:

### Data preprocessing

Obtain the correct source data, then run:

```
pipenv run preprocess.py
```

### Deploying

Apps run via WSGI containers on AWS.

Before deploying, make sure and run `pipenv run pip freeze > requirements.txt` to lock current versions of everything.

```
eb init
eb create # if needed to create environment
eb deploy
```

### Journal graphics version

The branch `journal_graphics` has changes to support the specific formatting for the charts for journal publication.
