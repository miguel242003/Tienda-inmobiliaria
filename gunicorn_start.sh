#!/bin/bash

NAME="tienda_inmobiliaria"
DIR=/home/deploy/Tienda-inmobiliaria
USER=deploy
GROUP=deploy
WORKERS=3
BIND=unix:/home/deploy/Tienda-inmobiliaria/gunicorn.sock
DJANGO_SETTINGS_MODULE=tienda_meli.tienda_meli.settings
DJANGO_WSGI_MODULE=tienda_meli.tienda_meli.wsgi
LOG_LEVEL=error

cd $DIR
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DIR:$PYTHONPATH

# 🔥 CONFIGURACIÓN MÍNIMA Y FUNCIONAL
exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=- \
  --timeout 600
