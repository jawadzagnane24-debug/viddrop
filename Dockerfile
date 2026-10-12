FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask yt-dlp gunicorn
ENV PORT=3000
EXPOSE 3000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} app:app"]
