while True:
    import os
    import time
    output = os.popen('cd; netstat -lnt | grep 8000').read()
    if output == '':
        time.sleep(20)
        os.system(' cd /home/tim/core/; python /home/tim/core/manage.py runserver 0.0.0.0:8000')
