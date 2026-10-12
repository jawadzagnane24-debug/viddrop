
FROM python:3.11-slim

WORKDIR /app

ENV HOME=/tmp
ENV PORT=3000

COPY . .

RUN pip install --no-cache-dir flask yt-dlp gunicorn

EXPOSE 3000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} app:app"]
