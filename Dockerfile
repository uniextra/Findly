FROM python:3.11-slim

WORKDIR /app

# Create non-root user and group (UID/GID 1000)
RUN groupadd -r findly -g 1000 && \
    useradd -r -u 1000 -g findly -d /app -s /sbin/nologin findly

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directory exists and assign ownership to non-root user
RUN mkdir -p /app/data && chown -R findly:findly /app

USER findly

EXPOSE 8000

CMD ["python", "main.py"]
