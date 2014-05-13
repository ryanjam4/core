while True:
    import os
    import time
    output = os.popen('netstat -lnt | grep').read()
    if output == '':
        time.sleep(20)
        os.system('python /home/tim/core/manage.py runserver 0.0.0.0:8000')
