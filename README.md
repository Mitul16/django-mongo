# django-mongo
Django backend API with MongoDB, imitating Google Forms in a limited way, allowing for CRUD operations for forms via CSV format.

## Setup
> Please refer to the [Requirements](https://github.com/Mitul16/django-mongo#requirements) first

### Create a virtual environment
```bash
virtualenv venv
source ./venv/bin/activate
```

### Install the packages
```bash
pip install -r requirements.txt
```

### Start the servers
```bash
# start the `mongod` daemon or use a MongoDB server
mongod

# start the `django` server
python forms/manage.py runserver
```

> If using a MongoDB server, update the [settings.py](./forms/forms/settings.py) file

## Usage
Please refer to the [Postman collection](./docs/Forms.postman_collection.json)

## Requirements
- `python3.9+`
- `virtualenv`
- `pip3`
- `mongod` or a MongoDB Server
