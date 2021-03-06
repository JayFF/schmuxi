#-----Pretreatment--------------
#---This script cleans the data in the source-path (see spec_config.yml) and copies to
#---the target-path.
#---Included: Replacement of ( , --> . ). Dropping of columns and rows, that are not needed.
#---It also updates the automatic parameter-section in spec_config.yml (Not Yet):w

import os
from os import chdir
import yaml
from glob import glob
import re
config_source = "spec_config.yml"

with open(config_source, 'r') as configfile:
    cfg = yaml.load(configfile)
    
    if __name__=='__main__':
        source = cfg["general"]["source_path"]
        target = cfg["general"]["working_dir"]
        chdir(source)
        files_list = glob('*txt')


def replace_garbage(source, target, files):
    """cleans up spectral files"""
    old_directory = os.getcwd()
    chdir(source)
    for a_file in sorted(files):
        print('opening target ' + a_file)
        with open(target + a_file,'w') as new_file:
            print('opening source')
            with open(source + a_file) as old_file:
                print('opened source')
                for line in old_file:
                    #print('next line')
                    next_line = line
                    next_line = next_line.replace(',','.')
                    next_line = re.sub(r"\t1\t1\t"," ", next_line)
                    next_line = re.sub(r"\t1\t"," ", next_line)
                    new_file.write(next_line)

    chdir(old_directory)

if __name__ == '__main__':
    replace_garbage(source, target, files_list)
