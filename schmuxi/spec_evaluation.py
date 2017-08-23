import numpy as np
import pandas as pd
import yaml
from glob import glob
from os import chdir
import matplotlib.pyplot as plt
import re
from autofind_paras import find_parameters

#configuration file, that is searched for in the same folder. Includes manually set parameters, including paths.
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
    reference = cfg["reference"]["name"]

#loads a txt-file and parses a pandas-Dataframe
def load_file(filename):
    data = pd.read_csv(filename,seperator,header = None)
    return(data)

#identifies spectra by checking if the word "DCmap" is not in the file-name, which would identify a map.
def list_of_spectra(source):

    #change to directory of the source-files
    chdir(source)

    #create a list of all txt-files in the folder
    files_list = glob('*.txt')

    #check if files include the word "DC-map", indicating a map, not a single spectrum.
    spec_list = [entry for entry in files_list if "DCmap" not in entry]
    
    #returns a list of files, that sould only include spectra. As of now it includes every txt.-file that does 
    #not identify itself as a DC-Map.
    return(spec_list)

#def background

#Find cosmic peaks and replace with average of distant neigbours
def cosmic_erase(data, cosmic_repetition, cosmic_distance, cosmic_factor):

    for i in range(cosmic_repetition):
        print(data.idxmax()[1])
        print(data.iat[data.idxmax()[1]+cosmic_distance,1])
        if data.iat[data.idxmax()[1],1] > cosmic_factor * data.iat[data.idxmax()[1]+cosmic_distance,1]:
            data.set_value(data.idxmax()[1], list(data)[1], (data.iat[data.idxmax()[1]-cosmic_distance,1] + data.iat[data.idxmax()[1]+cosmic_distance,1]))
    
    return(data)

def plot_spectrum(spec, cfg, source):

    #use auto_parameters.py to find parameters in the file name
    parameters = find_parameters(spec, cfg)

    #load data
    #data = pd.read_csv(source + spec)
    data = load_file(source + spec)

    data.columns = ["Wavelength [nm]","Intensity [arb.]"]
    #data = data.set_index("Wavelength [nm]")
    print(data.head(5))

    data['Intensity [arb.]'] = data['Intensity [arb.]'] - background

    data = cosmic_erase(data, cosmic_repetition, cosmic_distance,
            cosmic_factor)    


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
    
    #print(reference_plot.head(5))
    #data = pd.concat([data,
    #    reference_plot], axis=1)
    #print(data.head(1000))
    #data = data.fillna(0).astype(float)
    plt.style.use('classic')
    #plot_data = data.plot.line(legend=False)
    plot_data = data.plot.line()
    
    if cfg["reference"]["use"] == ('TRUE' or 'true' or 'True'):
        print(source + reference)
        reference_plot = load_file(source + reference)
        reference_plot.columns = ["Energy","Intensity"]
        reference_plot["Energy"] = reference_plot["Energy"] + cfg["reference"]["offset"]
        reference_plot.set_index(list(reference_plot)[0], inplace=True)
        reference_plot.plot(ax=plot_data)

        mylabels = [cfg["reference"]["plot_name"], cfg["reference"]["ref_name"]]
        plot_data.legend(labels=mylabels)

    plot_data.set_xlabel(data.index.name)
    plot_data.set_ylabel(list(data)[0])
    yloc = plt.MaxNLocator(3)
    plot_data.yaxis.set_major_locator(yloc)
    print(data.index[0])
    
    plot_data.set_xlim(left=data.index[0], right=data.index[-1])
    
    count = 0
    for i, j in parameters.items():
        plt.text(data.index[10],data.max()*(0.95-0.05*count), i)
        plt.text(data.index[300],data.max()*(0.95-0.05*count), j)
        count = count + 1
        print(count)
    fig = plot_data.get_figure()
    fig.savefig(spec[:-4] + '.png')

#This method goes through the target-folder, stated in the config-file (which should include only pretreated files)
#and plots every spectrum to an image file. It adjusts according to specifications in the config file and uses
#autofind_paras.py to find every experimental parameter from the name of the txt-file.
def plot_all_spectra(source):
    

    #iterate over all txt-files, that  are identified as spectra.
    for spec in list_of_spectra(source):

        plot_spectrum(spec, cfg, source)

if __name__ == '__main__':
    plot_all_spectra(source)
