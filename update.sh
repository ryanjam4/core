kill -9 $(pidof manage)
kill -9 $(pidof python)
cd
rm -rf core
kill -9 $(pidof manage)
kill -9 $(pidof python)
git clone https://github.com/ryanjam4/core.git
cd core
python manage.py syncdb
kill -9 $(pidof manage)
kill -9 $(pidof python)
python manage.py runserver 0.0.0.0:8000
kill -9 $(pidof manage)
kill -9 $(pidof python)
python manage.py runserver 0.0.0.0:8000
