'''Interactive tool, to identify phonon replicas'''
import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import curdoc, gridplot, figure, show, output_file
from bokeh.layouts import column
from bokeh.models import Button, TapTool, Slider
from bokeh.events import Tap
from spec_evaluation import Experiment

with open("spec_config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

with open("phonons.yml", 'r') as phonon_file:
    phonons = yaml.load(phonon_file)
Session = Experiment()


spectra = [Session.prepare_spectrum(Session.spectra[i[0]]) for i in enumerate(Session.spectra)]

TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

spec = figure(width=1000, height=700, tools=TOOLS)

r = spec.line(x=[],y=[], line_color="blue")
ds = r.data_source

Material = "WS2"
Layer = "Monolayer"

#def switch_calibration():
#
#    global x_axis
#    x_axis = 1239.8/x_axis

spec_slider = Slider(start=0, end=len(spectra)-1, value=0, step=1,
        title="Freeze Hell!")

#test
K_energy = 2.085
#Q_pos = 2.1

K_phonons = [K_energy-phonon/1000 for phonon in
        list(phonons[Material][Layer]["K"].values())]
#Q_phonons = [Q_energy-phonon/1000 for phonon in phonons[Material][Layer]["Q"]]

K_phonons_nested = [K_phonons[i:i+1] * 2 for i,j in enumerate(K_phonons)]
K_phonons_nested.append([K_energy,K_energy])
K_y_values = [[0,3] for i,j in enumerate(K_phonons)]
K_y_values.append([0,3])

spec.multi_line(K_phonons_nested, K_y_values, line_width=1)

def display_spectrum(attr, old, new):
    '''plots spectrum, selected in the slider'''
    new_data = dict()
    current_spec = spectra[spec_slider.value]
    x_axis = current_spec.index.tolist()
    new_data["x"] = x_axis
    new_data["y"] = current_spec[list(current_spec)[0]].tolist()
    ds.data = new_data

def adjust_replica(attr, old, new):
    '''display of phonon replica adjusted through position of valleys'''
    

spec_slider.on_change('value', display_spectrum)

panel = gridplot([[spec]])
curdoc().add_root(column(panel,spec_slider))
