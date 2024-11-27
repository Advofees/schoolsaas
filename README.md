## Development

### Setup

- You will need to have

  - Python 3.10
  - Docker
  - task go `https://taskfile.dev/`
  
- Open a terminal in the root of this repository

- Create a Python virtual environment:

  ```bash
  python3 -m venv venv
  ```

- Activate the Python environment:

  ```bash
  source venv/bin/activate
  ```

  - For Windows and git bash users

    ```bash
    source venv/Scripts/activate
    ```

- Install dependencies

  ```bash
  pip install -r requirements.txt
  ```
- start docker for local development
  ````
  docker compose -f infrastructure_services/docker-compose.dev.yml up
  ```
- Run migrations

  ```bash
  ./run-migrations.sh
  ```

- To generate migrations make sure the model is added in backend/database/all_models.py then run the following commands

  ```bash
  ./generate-migrations
  ./run-migrations.sh
  ```
- seed database

  ```bash
  ./seed-database.sh
  ```
- run server

  ```bash
   ./backend/start.dev.sh
   ````
   or 

  ```bash
  
  task server
  ```
