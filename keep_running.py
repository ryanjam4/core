while True:
    import os
    import time
    print 'Netstat'
    output = os.popen('cd /home/tim/core/; netstat -lnt | grep 8000').read()
    if output == '':
        print 'Sleeping 20 seconds'
        time.sleep(20)

        os.system(' cd /home/tim/core/; python /home/tim/core/manage.py runserver 0.0.0.0:8000')
    else:
        print 'Sleeping 1 second'
        time.sleep(1)
