# ChatWithDB

ChatWithDB is an innovative project that transforms traditional databases into conversational partners using LLMs and
Django. It accepts user input, finds similar database entries, and crafts human-like responses using OpenAI's GPT-3.5 or different LLMs,
creating a unique interaction experience with databases. The project supports multiple databases, including PostgreSQL
and MySQL.

## Features

- User-friendly Django admin dashboard to manage database connections.
- Integration with OpenAI's GPT-3 or Different LLMs to process user queries and responses.
- Advanced text similarity search with different databases.
- APIs to facilitate user interaction with databases.

## Installation

First, clone the repository:

```sh
git clone https://github.com/shamspias/ChatWithDB.git
cd ChatWithDB
```

Install related pack

```shell
sudo apt-get install python3-dev python3-venv libcurl4-openssl-dev gcc libssl-dev -y
```

Create and active virtual environment

#### Linux & MAC

```shell
python3 -m venv venv
. venv/bin/activate
```

#### Windows

```shell
python -m venv venv
. venv/Scripts/activate
```

Install the required Python packages:

```sh
pip install -r requirements.txt
```

Configure your database in `settings.py`, then apply migrations:

```sh
python manage.py makemigrations
python manage.py migrate
```

Start the Django Celery server:

```sh
celery -A config worker --loglevel=info
```

Start the Django development server:

```sh
python manage.py runserver
```

The server should be running on `localhost:8000`.

## Usage

Navigate to the Django admin dashboard to add or manage your databases. Then, use the provided APIs to interact with
your database. Enter your query, and the system will find similar entries in the database and craft a human-like
response using GPT-3.5 or different LLMs.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE.md) file for details.

```