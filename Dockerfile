FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY config.py ./
COPY src/ src/
COPY models/model.joblib models/metadata.json models/
RUN python -c "from src.inference import load_model; load_model()"
CMD ["python", "-m", "src.main"]
