import numpy as np
import pandas as pd
import yaml
from scipy.optimize import curve_fit

default_models = "fit_models.yml"


def ensemble(base_function, *param_sets):
    return(sum([base_function(x, p) for p in param_sets]))


def lorentz(x, *parameters):


def gauss(x, *parameters):
    A, mu, sigma = parameters
    return(A*numpy.exp(-(x-mu)**2/(2.*sigma**2)))


class FitAnalysis:
    

    def load_file(self, source):
        with open(source, "r") as yaml_file:
            cfg = yaml.load(yaml_file)
        return(cfg)

    
    def phonon_model(self, 
                     material="WSe2",
                     layers="Monolayer",
                     source="phonons.yml",):
        source = self.load_file(source)
    

    def exciton(self, 
                data,
                energy,
                bounds=None,
                base_function=lorentz):
        popt, pcov = curve_fit(base_function, data[0], data[1]

    

    def __init__(self, 
                 model=None,
                 model_source=default_models):
        self.model = model
        self.startvalues = parameters


    def fit(self):
        self.parameters


    def set_model(self, model=None):
        self.model = model

