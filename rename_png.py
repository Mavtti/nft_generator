import os

for p,d, fs in [(p,d,files) for p,d,files in os.walk('./images/') if not d]:
    for f in fs:
        if '.PNG' in f:
            os.rename(p+'/'+f, p+'/'+f.replace('.PNG', '.png'))
