FROM python:3.10-slim

WORKDIR /app

# Install build deps and pip requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Initialize the database at build time (so app.db exists)
RUN python db_init.py

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
