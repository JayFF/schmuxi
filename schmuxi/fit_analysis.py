import numpy as np
import pandas as pd
import yaml
from scipy.optimize import curve_fit

default_models = "fit_models.yml"


class FitAnalysis:
    

    def load_model(self, model_source):
        with open(model_source, "r") as model_file:
            model_cfg = yaml.load(model_file)
        return(model_cfg)


    def __init__(self, 
                 model=None,
                 model_source=default_models):
        self.model = model

        self.startvalues = parameters


    def fit(self):
        self.parameters


    def set_model(self, model=None):
        self.model = model


def ensemble(self, base_function, *param_sets):
    return(sum([base_function(x, p) for p in param_sets]))


def lorentz(self, x, *parameters):


def gauss(self, x, *parameters):
    A, mu, sigma = parameters
    return(A*numpy.exp(-(x-mu)**2/(2.*sigma**2)))
