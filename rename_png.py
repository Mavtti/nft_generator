import os
import unicode

for p,d, fs in [(p,d,files) for p,d,files in os.walk('./images/') if not d]:
    for f in fs:
        old_file_name = p+'/'+f
        if '.PNG' in f:
            new_file_name = p+'/'+f.replace('.PNG', '.png')
            os.rename(old_file_name, new_file_name)
            old_file_name = new_file_name
        os.rename(old_file_name, unidecode.unidecode(accented_string))
