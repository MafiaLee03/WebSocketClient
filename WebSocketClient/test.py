import time

a = ['k','w']
start_time = time.time()
while 'n' not in a:
    print('n not in a')
    cost_time = time.time() - start_time
    if cost_time >= 15:
        a.append('n')