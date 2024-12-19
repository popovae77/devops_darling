FROM python:3.12-slim
RUN python3 -m venv /opt/venv

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 3000

CMD ["python", "main.py"]