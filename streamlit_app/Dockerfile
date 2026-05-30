FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app/ ./streamlit_app/

EXPOSE 8501

# Adjust Streamlit default settings to allow headless network execution strings
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
