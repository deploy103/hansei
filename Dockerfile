FROM python:3.13-alpine
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=8004
WORKDIR /app
COPY --chown=65532:65532 hansei_server.py hansei.html hansei.css hansei.js hansei.webmanifest favicon.svg hansei_logo.jpg ./
USER 65532:65532
EXPOSE 8004
CMD ["python", "hansei_server.py"]
