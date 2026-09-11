FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY superkart_model.joblib .

EXPOSE 7860

CMD ["uvicorn", "app:superkart_api", "--host", "0.0.0.0", "--port", "7860"]
