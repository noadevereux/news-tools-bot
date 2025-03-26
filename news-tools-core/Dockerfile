FROM python:3.11-alpine3.21
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
RUN alembic init alembic
COPY docker-assets/alembic-env.py alembic/env.py
RUN sed -i 's|sqlalchemy.url = .*|sqlalchemy.url = mysql+mysqlconnector://${MYSQL_USER}:${MYSQL_PASSWORD}@database/${MYSQL_DATABASE}|g' alembic.ini
RUN if [ ! -f alembic/versions/*.py ]; then alembic revision --autogenerate -m 'initial revision'; fi
RUN alembic upgrade head
ENTRYPOINT ["python3", "main.py"]