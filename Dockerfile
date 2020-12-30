FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:create_app()" ]

EXPOSE 8000