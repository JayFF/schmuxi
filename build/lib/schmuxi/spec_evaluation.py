'''Turns your raw txt-data of spectra into graphics & reports for your labbook or
publication
'''
# import numpy as np
import pandas as pd
import yaml
from glob import glob
from os import chdir
import os
import matplotlib.pyplot as plt
import re
from schmuxi.autofind_paras import find_parameters
import logging

default_config = "spec_config.yml"


class Experiment:
    '''Represents an experimental session and contains parameters and methods
    to process and publish its results'''

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
        """loads yml-file and returns it as configuration-dictionary"""
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
        convert_to_energy = True,
        convert_to_rate = True,
        normalize = False,
        exposure = 0,
        cosmic_cycles = 5,
        cosmic_factor = 10,
        cosmic_distance = 5,
        reference = None):
        '''initializies experimental parameters and
        processes configuration.'''

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
                self.convert_to_energy = True if config["spec_paras"]["convert_to_energy"].upper() == 'TRUE' else False
                self.convert_to_rate = True if config["spec_paras"]["convert_to_rate"].upper() == 'TRUE' else False
                self.normalize = True if config["spec_paras"]["normalize"].upper() == 'TRUE' else False
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

                self.reference = reference
        self.spectra = self.list_of_spectra(self.working_dir)


    def change_working_dir(self, place=os.getcwd()):
        '''changes working directory for the expriment'''
        self.working_dir = place
        print(self.working_dir)


    def load_file(self, filename):
        '''reads a csv-file into a pandas.Dataframe'''
        spectrum = pd.read_csv(filename, self.seperator, header=None)

        return(spectrum)


    def list_of_spectra(self, source):
        '''Checks the filenames of txt-files to find Data corresponding to single
        spectra.'''
        chdir(source)
        files_list = glob('*.txt')

        # does not include spectral maps.
        spectra = [entry for entry in files_list if "DC" not in entry]

        return(spectra)
    

    def list_of_maps(self, source):
        '''Checks the filenames of txt-files to find Data corresponding to
        spectral maps.'''
        chdir(source)
        files_list = glob('*.txt')
        maps = [entry for entry in files_list if re.match('.*DC.*map.*', entry)]
        return(maps)


    def adjust_background(self, spectrum):
        '''Subtracts background from signal, as specified in the
        configuration'''
        
        try:
            spectrum.ix[:, 1] = spectrum.ix[:, 1] - self.background
        except:
            # catches the case, that the wavelength/energy has become the index
            print('already indexed')
            spectrum.ix[:, 0] = spectrum.ix[:, 0] - self.background
        finally:
            return(spectrum)
        

    def cosmic_erase(
        self,
        spectrum,
        cosmic_cycles,
        cosmic_distance,
        cosmic_factor):
        '''Routine for erasing "cosmics", random high intensity peaks'''
        for i in range(cosmic_cycles):
            if spectrum.iat[spectrum.idxmax()[1], 1] > cosmic_factor * spectrum.iat[spectrum.idxmax()[1]+cosmic_distance, 1]:
                spectrum.set_value(spectrum.idxmax()[1],
                                   list(spectrum)[1],
                                   (spectrum.iat[spectrum.idxmax()[1]-cosmic_distance,1] + spectrum.iat[spectrum.idxmax()[1]+cosmic_distance, 1]))
        return(spectrum)
    
 
    def adjust_scale(self, spectrum, spec=None, exposure=None):
        '''Calculates and names the x and y scale according to the
        configuration'''
        if self.convert_to_energy is True:
            spectrum.rename(columns={list(spectrum)[0]: 'Energy [eV]'}, inplace=True)
            spectrum['Energy [eV]'] = 1239.82/spectrum['Energy [eV]']
            spectrum = spectrum.sort_values("Energy [eV]", axis=0)
            spectrum.set_index("Energy [eV]", inplace=True)
        else:
            spectrum.rename(columns={list(spectrum)[0]: 'Wavelength [nm]'},
                    inplace=True)
            spectrum.set_index("Wavelength [nm]", inplace=True)
        
        if self.normalize is True:
            spectrum.rename(columns={list(spectrum)[0]: "Intensity [norm.]"}, inplace=True)
            spectrum = spectrum/spectrum.max()
        elif self.convert_to_rate is True and (spec is not None):
            if re.match(".*[0-9]+s.*", spec):
                exposure = float(re.search("[0-9]+s", spec).group()[:-1])
                print(exposure)
            spectrum.rename(columns={list(spectrum)[0]: "Counts p.s."}, inplace=True)
            spectrum = spectrum/exposure

        return(spectrum)


    def adjust_spectrum(self, spectrum, spec=None):
        '''cleans prepares the given spectral dataframe for plotting in
        accordance with the configuration-file'''
        
        # Erase Background
        spectrum = self.adjust_background(spectrum)
        
        # Erase Cosmics (work in progress)
        spectrum = self.cosmic_erase(
            spectrum,
            self.cosmic_cycles,
            self.cosmic_distance,
            self.cosmic_factor)

        # Convert to Energy
        spectrum = self.adjust_scale(spectrum, spec, self.exposure)
        
        return(spectrum)
    

    def prepare_spectrum(self, spec):
        '''Uses load_file and adjust_spectrum to prepare a dataframe'''
        spectrum = self.load_file(self.working_dir + spec)
        spectrum = self.adjust_spectrum(spectrum, spec)
        return(spectrum)


    def plot_spectrum(self, spectrum, parameters=dict()):
        '''plots a single spectrum into png-file of the same name, according to the experimental configuration.'''
        plt.style.use('classic')
        plot_spectrum = spectrum.plot.line(legend=False)
        #plot_spectrum = spectrum.plot.line()

        if self.config["reference"]["use"] is ('TRUE' or 'true' or 'True'):

            reference_plot = self.load_file(self.working_dir + self.reference)
            reference_plot.columns = ["Energy","Intensity"]
            reference_plot["Energy"] = reference_plot["Energy"] + config["reference"]["offset"]
            reference_plot.set_index(list(reference_plot)[0], inplace=True)
            reference_plot.plot(ax=plot_spectrum)

            mylabels = [config["reference"]["plot_name"], config["reference"]["ref_name"]]
            plot_spectrum.legend(labels=mylabels)

        plot_spectrum.set_xlabel(spectrum.index.name)
        plot_spectrum.set_ylabel(list(spectrum)[0])
        yloc = plt.MaxNLocator(3)
        plot_spectrum.yaxis.set_major_locator(yloc)

        plot_spectrum.set_xlim(left=spectrum.index[0], right=spectrum.index[-1])
        spread = spectrum.values.max()-spectrum.values.min()
        plot_spectrum.set_ylim(spectrum.values.min() - 0.02 * spread,
                                spectrum.values.max() + 0.02 * spread)
        

        # PLEASE find a more beautiful way.
        count = 0
        for i, j in parameters.items():
            plt.text(spectrum.index[10],spectrum.max()*(0.95-0.05*count), i)
            plt.text(spectrum.index[300],spectrum.max()*(0.95-0.05*count), j)
            count = count + 1
            print(count)

        return(plot_spectrum)


    def plot_to_png(self, plot_spectrum, spec):
        '''Saves matplotlib-plot into png-file, given a name. Cuts off the last
        4 characters to eliminate file-endings.'''
        fig = plot_spectrum.get_figure()
        fig.savefig(spec[:-4] + '.png')


    def save_as_csv(self, spectrum, spec):
        '''Writes spectrum-dataframe into csv-file, given a name minus the last
        4 characters to eliminate file endings.'''
        spectrum.to_csv(spec[:-4] + '.csv')


    def plot_in_one(self, spectra):
        '''plots a list of spectra in a single figure.'''
        list_of_spectra = [self.prepare_spectrum(spec) for spec in spectra]
        joined_spectra = pd.concat(list_of_spectra, axis=1)
        plot = joined_spectra.plot.line(legend=False)
        return(plot)


    def plot_at_once(self):
        '''One-Click-function to publish e1very spectrum in the working
        directory into a single graph (not recommended)'''
        plot = self.plot_in_one(self.spectra)
        self.plot_to_png(plot, "Summary")


    def plot_all_spectra(self):
        '''"One-Click"-function to publish every spectrum in the
        working-directory into single images.'''
        for spec in self.spectra:
            parameters = find_parameters(spec, self.config)
            spectrum = self.prepare_spectrum(spec)
            plot = self.plot_spectrum(
                    spectrum,
                    parameters)
            self.plot_to_png(plot, spec)



if __name__ == '__main__':
    Session = Experiment()
    Session.plot_all_spectra()
    #Session.plot_all_spectra()
