# import numpy as np
import pandas as pd
import yaml
from glob import glob
from os import chdir
import os
import matplotlib.pyplot as plt
import re
from autofind_paras import find_parameters


default_config = "spec_config.yml"


class Experiment:

    def auto_config(self, config_source):
    """creates a dictionary of configuration parameters out of given path"""
        config = None

        # fallback to default config if no file can be found
        try:
            config = self.load_config(config_source)
        except IOError:
            print("No configuration-file found. Using default-configuration.")
            try:
                config = self.load_config(os.path.dirname(os.abspath(__file__))+"/"+default_config)
            except IOError:
                print("Someone messed with the default-configuration file. It cannot be found.")
            else: return(config)
        else: return(config)


    def load_config(self, config_source):
    """loads yml-file and turns it into a dict"""
        with open(config_source, 'r') as configfile:
            config = yaml.load(configfile)

        return(config)

    def __init__(
        self,
        auto_config = True,
        config_source = "spec_config.yml",
        source = os.getcwd(),
        working_dir = os.getcwd(),
        seperator = " ",
        background = 0,
        convert_to_energy = "TRUE",
        convert_to_rate = "TRUE",
        normalize = "FALSE",
        exposure = 0,
        cosmic_cycles = 5,
        cosmic_factor = 10,
        cosmic_distance = 5,
        reference = None):


        if auto_config is True:

            try:
                config = self.auto_config(config_source)
            except:
                print("Auto-Configuration failed.")
            else:
                self.config = config
                self.working_dir = config["general"]["working_dir"]
                self.seperator = config["spec_paras"]["seperator"]
                self.background = config["spec_paras"]["background"]
                self.convert_to_energy = config["spec_paras"]["convert_to_energy"]
                self.convert_to_rate = config["spec_paras"]["convert_to_rate"]
                self.normalize = config["spec_paras"]["normalize"]
                self.source = config["general"]["source_path"]
                self.exposure = config["spec_paras"]["exposure"]

                self.cosmic_cycles = config["auto_paras"]["cosmic_cycles"]
                self.cosmic_factor = config["auto_paras"]["cosmic_factor"]
                self.cosmic_distance = config["auto_paras"]["cosmic_distance"]

                self.reference = config["reference"]["name"]
        else:
                self.working_dir = working_dir
                self.seperator = seperator
                self.background = background
                self.convert_to_energy = convert_to_energy
                self.convert_to_rate = convert_to_rate
                self.normalize = normalize
                self.source = source
                self.exposure = exposure

                self.cosmic_cycles = cosmic_cycles
                self.cosmic_factor = cosmic_factor
                self.cosmic_distance = cosmic_distance

                self.reference = reference]

    def load_file(self, seperator=self.seperator, filename):

        data = pd.read_csv(filename, seperator, header=None)

        return(data)


def list_of_spectra(source):

        chdir(source)
        files_list = glob('*.txt')

        # does not include spectral maps.
        spec_list = [entry for entry in files_list if "DCmap" not in entry]

        return(spec_list)

# def background



def cosmic_erase(
    data,
    cosmic_cycles,
    cosmic_distance,
    cosmic_factor):

    for i in range(cosmic_cycles):
        if data.iat[data.idxmax()[1], 1] > cosmic_factor * data.iat[data.idxmax()[1]+cosmic_distance, 1]:
            data.set_value(data.idxmax()[1], list(data)[1], (data.iat[data.idxmax()[1]-cosmic_distance,1] + data.iat[data.idxmax()[1]+cosmic_distance, 1]))

    return(data)



def plot_spectrum(spec, cfg, source):

    #use auto_parameters.py to find parameters in the file name
    parameters = find_parameters(spec, cfg)

    #data = pd.read_csv(source + spec)
    data = load_file(source + spec)

    data.columns = ["Wavelength [nm]","Intensity [arb.]"]
    #data = data.set_index("Wavelength [nm]")
    print(data.head(5))

    data['Intensity [arb.]'] = data['Intensity [arb.]'] - background

    data = cosmic_erase(
        data,
        cosmic_cycles,
        cosmic_distance,
        cosmic_factor)


    if convert_to_energy == ('TRUE' or 'true'):
        print(list(data))
        data.rename(columns={"Wavelength [nm]": 'Energy [eV]'}, inplace=True)
        print(data.head(5))
        data['Energy [eV]'] = 1239.82/data['Energy [eV]']
        data = data.sort_values("Energy [eV]", axis=0)
        data.set_index("Energy [eV]", inplace=True)
    else:
        data.set_index("Wavelength [nm]", inplace=True)
    if normalize == ('TRUE' or 'true'):
        data.rename(columns={list(data)[0]: "Intensity [norm.]"}, inplace=True)
        data = data/data.max()
    elif convert_to_rate == ('TRUE' or 'true'):
        if re.match(".*[0-9]*s.*", spec):
            exposure = float(re.search("[0-9]*s", spec).group()[:-1])
            print(exposure)
        data.rename(columns={"Intensity [arb.]": "Counts p.s."}, inplace=True)
        data = data/exposure

    plt.style.use('classic')
    #plot_data = data.plot.line(legend=False)
    plot_data = data.plot.line()

    if cfg["reference"]["use"] == ('TRUE' or 'true' or 'True'):

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



def plot_all_spectra(source):

    for spec in list_of_spectra(source):
        plot_spectrum(spec, cfg, source)

if __name__ == '__main__':
    plot_all_spectra(source)
