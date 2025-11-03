FROM python:3.14.0-alpine AS python-base

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=2.2.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

ENV POETRY_CACHE_DIR=/opt/.cache

FROM python-base AS poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
  && $POETRY_VENV/bin/pip install -U pip setuptools \
  && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

FROM python-base AS embed-server

WORKDIR /app

# Add Poetry to PATH
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="${PATH}:${POETRY_VENV}/bin"

COPY poetry.lock pyproject.toml ./
RUN poetry check
RUN poetry install --no-interaction --no-cache --no-root

# runtime dependency
RUN apk add --no-cache ffmpeg

COPY . /app

VOLUME ["/app/files"]
EXPOSE 8080
CMD [ "poetry", "run", "waitress-serve", "--host", "0.0.0.0", "src.app.app" ]
