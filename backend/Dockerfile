FROM python:3.8

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY Koordinaten.json .

EXPOSE 5000

ENV FLASK_APP=influxdb_to_json.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]