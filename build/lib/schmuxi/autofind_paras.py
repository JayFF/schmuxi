import re
import yaml
from os import chdir
from glob import glob

config_source = "spec_config.yml"

def open_config(config):
    with open(config, 'r') as configfile:
        cfg = yaml.load(configfile)
    return(cfg)

#The following methods find parameters in the filename or reads it from the configfile

def find_exposure(spec, cfg):
    if re.match(".*[0-9]+[sS].*", spec):
        print(re.search("[0-9]+[sS]",spec).group()[:-1])
        return float(re.search("[0-9]+[sS]",spec).group()[:-1])
    else:
        return cfg["spec_paras"]["exposure"]

def find_excitation(spec, cfg):
    if re.match(".*[0-9]+nm.*", spec, re.IGNORECASE):
        return float(re.search("[0-9]+nm", spec, re.IGNORECASE).group()[:-2])
    else:
        return cfg["general"]["excitation"]

def find_bandwidth(spec, cfg):
    if re.match(".*bw[0-9]+nm.*", spec, re.IGNORECASE):
        return float((re.search("(bw|BW)[0-9]+nm", spec, re.IGNORECASE).group()[:-2])[2:]) 
    elif re.match(".*(\+-|-\+)[0-9]+nm.*", spec, re.IGNORECASE):
        return float((re.search("(\+-|-\+)[0-9]+nm", spec, re.IGNORECASE).group()[:-2])[2:])*2
    else:
        return cfg["general"]["bandwidth"]

def find_temperature(spec, cfg):
    if re.match(".*[0-9]+(K|k).*", spec):
        return float(re.search("[0-9]+(k|K)",spec).group()[:-1])
    else:
        return cfg["general"]["temperature"]

def check_if_map(spec, cfg):
    return re.match(".*(DCmap).*", spec, re.IGNORECASE)

def find_power(spec, cfg): #returns only the numerical value, NOT the unit
    if re.match(".*[0-9]+[a-z]?W.*", spec, re.IGNORECASE):
        power_word = re.search("[0-9]+[a-z]?W", spec, re.IGNORECASE).group()
        return float(re.search("[0-9]*",power_word).group())
    else:
        return cfg["general"]["power"]

def find_repetition(spec, cfg): #returns only the numerical value, NOT the unit
    if re.match(".*[0-9]+[a-z]hz.*", spec, re.IGNORECASE):
       repetition_word = re.search("[0-9]+[a-z]?hz", spec, re.IGNORECASE).group()
       return float(re.search("[0-9]*",repetition_word).group())
    else:
        return cfg["general"]["repetition"]

#work in progress
#def find_material(spec, cfg):
    #if re.match(".

def find_parameters(spec, cfg):
    parameters = {}
    parameters["exposure"] = find_exposure(spec, cfg)
    parameters["excitation"] = find_excitation(spec, cfg)
    parameters["bandwidth"] = find_bandwidth(spec, cfg)
    parameters["temperature"] = find_temperature(spec, cfg)
    #parameters["map"] = check_if_map(spec, cfg)
    parameters["power"] = find_power(spec, cfg)
    parameters["repetition"] = find_repetition(spec, cfg)
    return parameters

def main():
    cfg = open_config(config_source)
    source = cfg["general"]["target_path"]
    files_list = glob('*.txt')
    print(files_list)
    for spec in files_list:
        print(find_parameters(spec, cfg))

if __name__ == '__main__':
    main()
