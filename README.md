Django Event Portal - Quickstart
--------------------------------

1. Create & activate a virtualenv:
   python -m venv venv
   source venv/bin/activate   (Linux / macOS)
   venv\Scripts\activate     (Windows)

2. Install requirements:
   pip install -r requirements.txt

3. Run migrations, create superuser and start server:
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver

4. Access admin at http://127.0.0.1:8000/admin/
   Register via http://127.0.0.1:8000/register/

Notes:
- MEDIA files (profile images) are stored in /media/; DEBUG=True serves them automatically.
- Update SECRET_KEY in eventportal/settings.py before production.
- The API endpoints are under /api/ ...
