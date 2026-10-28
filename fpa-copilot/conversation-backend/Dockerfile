FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 HF_HOME=/opt/aria-models
RUN apt-get update && apt-get install -y --no-install-recommends espeak-ng libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY fpa-copilot/conversation-backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r /tmp/requirements.txt
RUN python -c "from kokoro import KPipeline; p=KPipeline(lang_code='a', device='cpu', repo_id='hexgrad/Kokoro-82M'); list(p('ARIA is ready.', voice='af_heart'))"
COPY fpa-copilot /app/fpa-copilot
RUN useradd --uid 10001 --create-home aria && chown -R aria:aria /opt/aria-models
USER aria
CMD ["python", "fpa-copilot/conversation-backend/server.py"]
