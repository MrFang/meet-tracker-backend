FROM python:3

WORKDIR /usr/src/app
ENV FLASK_ENV=production

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

RUN flask init-db

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:create_app()" ]

EXPOSE 8000
