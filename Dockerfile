FROM python:3.10

ARG USER_GID=1000
ARG USER_UID=1000

RUN groupadd --gid $USER_GID python && useradd --uid $USER_UID --gid $USER_GID --create-home python

ENV PATH="/home/python/.local/bin:${PATH}"

USER python

RUN mkdir -p /home/python/app 

WORKDIR /home/python/app

ENV PYTHONPATH=/home/python/app

COPY requirements.txt /home/python/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./backend/ /home/python/app/backend/
COPY ./alembic/ /home/python/app/alembic/

COPY ./backend/start.sh \
  ./alembic.ini \
  /home/python/app/

EXPOSE 8080

ARG GIT_COMMIT_SHA
ENV GIT_COMMIT_SHA="$GIT_COMMIT_SHA"

ENTRYPOINT [ "/bin/bash" ]
CMD ["./backend/start.sh"]