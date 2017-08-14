import numpy as np
import pandas as pd
import yaml
from glob import glob
from os import chdir
import matplotlib.pyplot as plt
import re

config_source =  "spec_config.yml"


with open(config_source, 'r') as configfile:
    cfg = yaml.load(configfile)
    source = cfg["general"]["target_path"]
    seperator = cfg["spec_paras"]["seperator"]
    background = cfg["general"]["background"]
    convert_to_energy = cfg["spec_paras"]["convert_to_energy"]
    convert_to_rate = cfg["spec_paras"]["convert_to_rate"]
    normalize = cfg["spec_paras"]["normalize"]
    exposure = cfg["spec_paras"]["exposure"]

def load_file(filename):
    data = pd.read_csv(filename,seperator,header = None)
    print(data.head(5))
    return(data)

def list_of_spectra(source):
    chdir(source)
    files_list = glob('*.txt')
    spec_list = [entry for entry in files_list if "DCmap" not in entry]
    print(files_list)
    print(spec_list)
    return(spec_list)

def main():
    for spec in list_of_spectra(source):
        data = load_file(source + spec)
        data.columns = ["Wavelength [nm]","Intensity [arb.]"]
        #data = data.set_index("Wavelength [nm]")
        print(data.head(5))
        data['Intensity [arb.]'] = data['Intensity [arb.]'] - background
        if convert_to_energy == ('TRUE' or 'true'):
            print(list(data))
            data.rename(columns={"Wavelength [nm]": 'Energy [eV]'}, inplace=True)
            print(data.head(5))
            data['Energy [eV]'] = 1239.82/data['Energy [eV]']
            data = data.sort_values("Energy [eV]",axis=0)
            data = data.set_index("Energy [eV]")
        else:
            data.set_index("Wavelength [nm]", inplace=True)
        
        if normalize == ('TRUE' or 'true'):
            data.rename(columns={"Intensity [arb.]": "Intensity [norm.]"}, inplace=True)
            data = data/data.max()
        elif convert_to_rate == ('TRUE' or 'true'):
            if re.match(".*-[0-9]*s-.*",spec):
                exposure = float(re.search("[0-9]*s",spec).group()[:-1])
                print(exposure)
            data = data/exposure

        data.plot.line()
        plt.show()

if __name__ == '__main__':
    main()
