FROM ghcr.io/nextgencontributions/python-dev-image

WORKDIR /app

COPY . .

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
