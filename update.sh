cd
rm -rf core
git clone https://github.com/ryanjam4/core.git
cd core
python manage.py syncdb
python manage.py runserver 0.0.0.0:8000
