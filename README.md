# ChatWithDB

ChatWithDB is an innovative project that transforms traditional databases into conversational partners using LLMs and Django. It accepts user input, finds similar database entries, and crafts human-like responses using OpenAI's LLMs, creating a unique interaction experience with databases. The project supports multiple databases, including PostgreSQL and MySQL.

## Features

- User-friendly Django admin dashboard to manage database connections.
- Integration with OpenAI's GPT-3 to process user queries and responses.
- Advanced text similarity search with different databases.
- APIs to facilitate user interaction with databases.

## Installation

First, clone the repository:

```sh
git clone https://github.com/shamspias/ChatWithDB.git
cd ChatWithDB
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

Start the Django development server:

```sh
python manage.py runserver
```

The server should be running on `localhost:8000`.

## Usage

Navigate to the Django admin dashboard to add or manage your databases. Then, use the provided APIs to interact with your database. Enter your query, and the system will find similar entries in the database and craft a human-like response using GPT-3.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE.md) file for details.
```