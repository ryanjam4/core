kill -9 $(pidof manage)
kill -9 $(pidof python)
cd
rm -rf core
git clone https://github.com/ryanjam4/core.git
cd core
python manage.py syncdb
netstat
python manage.py runserver 0.0.0.0:8000
