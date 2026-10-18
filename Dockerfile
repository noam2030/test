FROM python:3.12-slim
WORKDIR /app
COPY app.py index.html ./
ENV PORT=8080
CMD ["python", "app.py"]
