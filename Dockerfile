# Dockerfile for the Streamlit app
FROM python:3.12-slim

WORKDIR /app

# environment: where the Ollama API will be reachable from inside compose
ENV OLLAMA_HOST=http://ollama:11434

# minimal apt deps (keep image small)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

EXPOSE 8501

# run streamlit
CMD ["streamlit", "run", "web_agent.py", "--server.address=0.0.0.0", "--server.port=8501"]
