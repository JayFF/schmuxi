import numpy as np
import pandas as pd
import yaml
from glob import glob
from os import chdir
import matplotlib.pyplot as plt
import re
from autofind_paras import find_parameters

config_source =  "spec_config.yml"

# check the config-file for variables. Most are later replaced by automatically found parameters. (Can be adjusted for performance)
with open(config_source, 'r') as configfile:
    cfg = yaml.load(configfile)
    source = cfg["general"]["target_path"]
    seperator = cfg["spec_paras"]["seperator"]
    background = cfg["spec_paras"]["background"]
    convert_to_energy = cfg["spec_paras"]["convert_to_energy"]
    convert_to_rate = cfg["spec_paras"]["convert_to_rate"]
    normalize = cfg["spec_paras"]["normalize"]
    exposure = cfg["spec_paras"]["exposure"]
    cosmic_repetition = cfg["auto_paras"]["cosmic_repetition"]
    cosmic_factor = cfg["auto_paras"]["cosmic_factor"]
    cosmic_distance = cfg["auto_paras"]["cosmic_distance"]

#loads a txt-file and parses a pandas-Dataframe
def load_file(filename):
    data = pd.read_csv(filename,seperator,header = None)
    return(data)

#identifies spectra by checking if the word "DCmap" is not in the file-name, which would identify a map.
def list_of_spectra(source):
    chdir(source)
    files_list = glob('*.txt')
    spec_list = [entry for entry in files_list if "DCmap" not in entry]
    print(files_list)
    print("List of identified spectra:\n" + spec_list)
    return(spec_list)

def plot_all_spectra():

    #iterate over all txt-files, that  are identified as spectra.
    for spec in list_of_spectra(source):
        parameters = find_parameters(spec, cfg)
        data = load_file(source + spec)

        data.columns = ["Wavelength [nm]","Intensity [arb.]"]
        #data = data.set_index("Wavelength [nm]")
        print(data.head(5))
        data['Intensity [arb.]'] = data['Intensity [arb.]'] - background

        for i in range(cosmic_repetition):
            print(data.idxmax()[1])
            print(data.iat[data.idxmax()[1]+cosmic_distance,1])
            if data.iat[data.idxmax()[1],1] > cosmic_factor * data.iat[data.idxmax()[1]+cosmic_distance,1]:
                data.set_value(data.idxmax()[1], list(data)[1], (data.iat[data.idxmax()[1]-cosmic_distance,1] + data.iat[data.idxmax()[1]+cosmic_distance,1]))


        if convert_to_energy == ('TRUE' or 'true'):
            print(list(data))
            data.rename(columns={"Wavelength [nm]": 'Energy [eV]'}, inplace=True)
            print(data.head(5))
            data['Energy [eV]'] = 1239.82/data['Energy [eV]']
            data = data.sort_values("Energy [eV]",axis=0)
            data.set_index("Energy [eV]", inplace=True)
        else:
            data.set_index("Wavelength [nm]", inplace=True)
        if normalize == ('TRUE' or 'true'):
            data.rename(columns={list(data)[0]: "Intensity [norm.]"}, inplace=True)
            data = data/data.max()
        elif convert_to_rate == ('TRUE' or 'true'):
            if re.match(".*[0-9]*s.*",spec):
                exposure = float(re.search("[0-9]*s",spec).group()[:-1])
                print(exposure)
            data.rename(columns={"Intensity [arb.]": "Counts p.s."}, inplace=True)
            data = data/exposure
        print(data.head(5))
        plt.style.use('classic')
        plot_data = data.plot.line(legend=False)
        plot_data.set_ylabel(list(data)[0])
        yloc = plt.MaxNLocator(3)
        plot_data.yaxis.set_major_locator(yloc)
        count = 0
        for i, j in parameters.items():
            plot_data.text(data.index[10],data.max()*(0.95-0.05*count), i)
            plot_data.text(data.index[300],data.max()*(0.95-0.05*count), j)
            count = count + 1
            print(count)
        fig = plot_data.get_figure()
        fig.savefig(spec[:-4] + '.png')

if __name__ == '__main__':
    plot_all_spectra()
