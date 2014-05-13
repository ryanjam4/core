kill -9 $(pidof python)
cd
rm -rf core
git clone https://github.com/ryanjam4/core.git
cd core
python manage.py syncdb
sleep 20
python manage.py runserver 0.0.0.0:8000
