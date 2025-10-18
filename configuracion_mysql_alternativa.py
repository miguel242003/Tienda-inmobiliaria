
# Configuración alternativa para MySQL remoto
# Copia esto en settings.py si necesitas conexión directa

# OPCIÓN A: SSH Tunnel (ya configurado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tienda_inmobiliaria_prod',
        'USER': 'tienda_user',
        'PASSWORD': 'M@s_242003!',
        'HOST': '127.0.0.1',  # localhost a través del SSH tunnel
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# OPCIÓN B: Conexión directa al servidor
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tienda_inmobiliaria_prod',
        'USER': 'tienda_user',
        'PASSWORD': 'M@s_242003!',
        'HOST': 'TU_IP_SERVIDOR',  # Cambiar por la IP real
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
