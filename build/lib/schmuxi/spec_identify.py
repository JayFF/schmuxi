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

spec_curve = spec.line(x=[],y=[], line_color="blue")
replica = spec.multi_line(xs=[], ys=[], line_width=1, line_dash='dashed')
ds = spec_curve.data_source
ds2 = replica.data_source


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


#Q_phonons = [Q_energy-phonon/1000 for phonon in phonons[Material][Layer]["Q"]]


def adjust_k_phonons(k_energy, phonons):
    K_phonons = [k_energy-phonon/1000 for phonon in
        list(phonons[Material][Layer]["K"].values())]
    K_phonons_nested = [K_phonons[i:i+1] * 2 for i,j in enumerate(K_phonons)]
    K_phonons_nested.append([k_energy,k_energy])

    K_y_values = [[0,3] for i,j in enumerate(K_phonons)]
    K_y_values.append([0,3])

    return(K_phonons,K_phonons_nested,K_y_values)


def display_spectrum(attr, old, new):
    '''plots spectrum, selected in the slider'''
    new_data = dict()
    global current_spec
    current_spec = spectra[spec_slider.value]
    x_axis = current_spec.index.tolist()
    new_data["x"] = x_axis
    new_data["y"] = current_spec[list(current_spec)[0]].tolist()
    ds.data = new_data

k_slider = Slider(start=1.7, end=2.2, value=K_energy, step=0.0001,
                    title="Adjust magic")

k_fine_slider = Slider(start=(-0.05), end=0.05, value=0, step=0.00001,
title='finetune magic')

def adjust_replica(attr, old, new):
    '''display of phonon replica adjusted through position of valleys'''
    global K_energy
    K_energy = k_slider.value + k_fine_slider.value
    new_data = dict()
    new_data["xs"] = adjust_k_phonons(K_energy,phonons)[1]
    new_data["ys"] = adjust_k_phonons(K_energy,phonons)[2]
    ds2.data = new_data

def publish():
    '''Use spec_evaluation to export the current spectrum as png and txt'''
    plot = Session.plot_spectrum(current_spec) 
    Session.plot_to_png(plot, "Export")
    Session.save_as_csv(current_spec, "Export")
    print("Exported")
    print(Session.working_dir)

publish_button = Button(label="Fool Referees")
publish_button.on_click(publish)
spec_slider.on_change('value', display_spectrum)
k_slider.on_change('value', adjust_replica)
k_fine_slider.on_change('value', adjust_replica)
panel = gridplot([[spec]])
curdoc().add_root(column(panel,spec_slider,k_slider,k_fine_slider,
    publish_button))
