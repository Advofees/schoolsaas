FROM python:3.10

WORKDIR /usr/src/app

ENV PYTHONPATH=/usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./backend/ ./backend/
COPY ./alembic/ ./alembic/

COPY ./alembic.ini .

EXPOSE 8080

ARG GIT_COMMIT_SHA
ENV GIT_COMMIT_SHA="$GIT_COMMIT_SHA"

ENTRYPOINT [ "/bin/bash" ]
CMD ["./backend/start.sh"]