# PWSIris backend

Refactored (with Docker, GitHub actions and Postgres (previous SQLite) support) backend for streamer website (API for content management) and 2nd line twitch bot (API for twitch bots to implement complex custom logic)

## Desired further improvements
-   Login with Twitch
    -   Admin access for streamer and moderators
    -   User access for followers (games/videos/anime suggestions)
-   Separate twitch-bot logic to standalone bot, not api for another bots
-   Use Redis instead of "python-memory"
-   Visit statistics?
-   Changes and improvements that I haven't thought about yet, better docs and better code?)

## Quick (not really...) start

Docker setup:
-   Install and setup Postgres with schema (don't forget to allow connect from docker addr in pg_hba.conf and postgresql.conf if bridge docker mode)
-   Install docker
-   Create somewhere and fill config.yaml for secrets
-   Apply alembic to postgres db
-   Configure [secrets](https://github.com/mirakzen-secrets-manager/backend) (check config.py)
-   Build and run image (some params can be taken from GH-action, like mounting config-file)

Development setup:
-   Install and setup Postgres with schema
-   Setup virtual environment
    ```shell
    python3 -m virtualenv venv
    . venv/bin/activate
    pip3 install -U -r requirements.txt
    pip3 install -U -r requirements_for_developer.txt
    ```
-   Create and fill config/config.yaml for secrets
-   Configure [secrets](https://github.com/mirakzen-secrets-manager/backend) (check config.py)
-   Apply alembic via `export PWSI_DB_DSN=connection-string` and `alembic upgrade head`
-   Run `python3 app/main.py` (has optional arguments)

Some extras:
-   Maybe you need to setup Nginx's reverse_proxy

## Stack
-   Python3 + FastAPI (async) + uvicorn
-   PostgreSQL + SQLAlchemy (async)
-   Docker
