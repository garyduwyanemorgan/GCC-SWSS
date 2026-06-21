FROM python:3.12-slim

WORKDIR /srv

# Install the engine first (better layer caching), then the API.
COPY engine /srv/engine
RUN pip install --no-cache-dir /srv/engine[ptf]

COPY api/requirements.txt /srv/api/requirements.txt
RUN pip install --no-cache-dir -r /srv/api/requirements.txt

COPY api/app /srv/api/app
WORKDIR /srv/api

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
