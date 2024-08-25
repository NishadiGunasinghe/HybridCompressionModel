FROM python:alpine3.20

WORKDIR /app
COPY . .
RUN pip --no-cache-dir install --ignore-installed distlib -r requirements.txt

CMD ["python", "Main.py"]