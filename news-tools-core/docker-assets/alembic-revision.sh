#!/bin/sh

if [ ! -f /lib/news-alembic/versions/*.py ]; then
  alembic revision --autogenerate -m 'initial revision'
fi

alembic upgrade head

exec "$@"
