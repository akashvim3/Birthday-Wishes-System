#!/bin/bash
# entrypoint.sh

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
END

# Collect static files
python manage.py collectstatic --noinput

# Start server
exec "$@"
