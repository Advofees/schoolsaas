## Development

### Setup

- You will need to have

  - Python 3.10
  - Docker

- Optional tools
    - task go `https://taskfile.dev/`
  
- Open a terminal in the root of this repository

- Create a Python virtual environment:

  ```bash
  python3 -m venv venv
  ```
- Setup absolute imports
  ```bash
  echo "PYTHONPATH=$(pwd)" > .env
  ```
- copy the values in environment_variables.md and add them to the .env

- Activate the Python environment:

  ```bash
  source venv/bin/activate
  ```

- Install dependencies

  ```bash
  pip install -r requirements.txt
  ```
- start docker for local development
  ```bash
  docker compose -f infrastructure_services/docker-compose.dev.yml down
  docker compose -f infrastructure_services/docker-compose.dev.yml up
  ```
- Seed the database
  - ```bash

  ./seed-database.sh 

  ```
  - or 
  ```bash
   python3 dev/seeds/local_seed.py
  ```
  - Start server

  ```bash
   ./backend/start.dev.sh
   ````
   or 

  ```bash
  
  task server
  ```
  - sample user
    - email/identity: `school@app.com`
    - password: `password123`

- To generate migrations make sure the model is added in backend/database/all_models.py then run the following commands

  ```bash
  ./generate-migrations
  ./run-migrations.sh
  ```
