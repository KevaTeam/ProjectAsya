DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'asya',
        'USER': 'root',
        'PASSWORD': '%DATABASE_PASSWORD%',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'OPTIONS': {
        'charset': 'utf8mb4'
    },
}