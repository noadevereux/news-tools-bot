FROM python:3.11-alpine3.21
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
RUN alembic init /lib/news-alembic
COPY docker-assets/alembic-env.py /lib/news-alembic/env.py
ARG MYSQL_DATABASE
ARG MYSQL_PASSWORD
ARG MYSQL_USER
RUN sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = mysql+mysqlconnector://${MYSQL_USER}:${MYSQL_PASSWORD}@database/${MYSQL_DATABASE}|g" alembic.ini
RUN sed -i "s|script_location = .*|script_location = /lib/news-alembic|g" alembic.ini
COPY docker-assets/alembic-revision.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/alembic-revision.sh
ENTRYPOINT ["/usr/local/bin/alembic-revision.sh"]
CMD ["python3", "main.py"]
