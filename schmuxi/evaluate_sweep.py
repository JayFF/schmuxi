'''Interactive tool to evaluate spectral maps.
To use it use the following command:
    
bokeh serve --show evaluate_map.py

Make sure, you have a config_file with the right name in the same folder.'''
import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import curdoc, gridplot, figure, show, output_file
from bokeh.layouts import column
from bokeh.models import Button, TapTool, Slider
from bokeh.events import Tap
import scipy.io as sio
import pandas as pd
from spec_evaluation import Experiment


# --- Configration ---

with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

working_dir = cfg["general"]["working_dir"]
working_file = cfg["sweep_paras"]["file"]
calibration_wavelength = cfg["sweep_paras"]["calibration_wavelength"]
calibration_parameters = cfg["sweep_paras"]["calibration_parameters"]


# --- Function Declarations ---

def load_file(working_file, seperator="\t"):
    '''loads a .tsv-file and initializes the sweep-data'''
    data = pd.read_csv(working_dir + working_file, seperator)
    data_matrix = data.as_matrix()
    calibration_wave = pd.read_csv(working_dir + calibration_wavelength, '\t', header=None)
    calibration_wave_list = np.array(list(calibration_wave[0]))
    calibration_param = pd.read_csv(working_dir + calibration_parameters, '\t', header=None)
    calibration_param_list = np.array(list(calibration_param[0]))
    return(data_matrix,
           calibration_wave_list,
           calibration_pram_list)


def display_spectrum(event):
    '''Display the spectrum for the clicked/tapped point on the map'''
    new_data = dict()
    new_data["x"] = x2
    new_data["y"] = data3d[int(np.round(event.x)),int(np.round(event.y)),:]
    ds.data = new_data


def switch_calibration():
    '''switch between energy [eV] and wavelength [nm]'''
    global x2
    x2 = 1239.8/x2
    Session.convert_to_energy = not Session.convert_to_energy


def adjust_marker(attr, old, new):
    '''adjust the position of the marker'''
    new_data = dict()
    new_data["x"] = [min(x2)+marker_slider.value*(max(x2)-min(x2)), min(x2)+marker_slider.value*(max(x2)-min(x2))]
    new_data["y"] = [0,max(ds.data["y"])]
    ds2.data = new_data


def publish():
    '''publishes the currently displayed spectrum, using spec_evaluation.py'''
    # Bad things can happen here. Find out and fix!
    publish_x = ds.data["x"]
    publish_y = ds.data["y"]
    publish_data = pd.DataFrame({'index': publish_x, 'values': publish_y})
    spectrum = Session.adjust_spectrum(publish_data, 
                                       background=False,
                                       overwrite_exposure=True,
                                       overwrite_rescaling=True)
    plot = Session.plot_spectrum(spectrum)
    Session.plot_to_png(plot, 'Fake_News.png')


# --- Skript starts ---


sweep, calibration_wave, calibration_param = load_file(working_file)
x = calibration_wave
y = calibration_param
z = sweep
z = z/np.max(z)

Session = Experiment()
Session.convert_to_energy = False

x2=1239.8/calibration_wave


# --- Data Visualization ---

TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

sweep_figure = figure(width=500, height=500, x_range=(-1,len(x)), y_range=(-1,len(y)), tools=TOOLS)
spec = figure(width=500, height = 500, tools=TOOLS)

z_lines = [spec for spec in z]

colors = ["#%02x%02x%02x" % (int(r), int(r), int(r/2)) for r in np.around(255*z)]

square_size = 7.7 *50/max(dim_x, dim_y)
spec_map.scatter(x, y, marker="square", size=square_size, fill_color=colors,
        line_color=None, selection_fill_color="red", nonselection_fill_alpha=0.8,
        nonselection_fill_color="fill_color")
spec_map.on_event(Tap, display_spectrum)


# --- Interfaces ---

marker_start_x = np.median(x2)
r = spec.line(x=[],y=[], line_color="red")
marker = spec.line(x=[marker_start_x,marker_start_x],y=[0,10], line_color="green")
ds = r.data_source
ds2 = marker.data_source

marker_slider = Slider(start=0,
                       end=1,
                       value=0.5,
                       step=0.002,
                       title="Marker")
marker_slider.on_change('value', adjust_marker)

energy_wavelength = Button(label="Fuck this up")
energy_wavelength.on_click(switch_calibration)

publish_button = Button(label="Fool Referees")
publish_button.on_click(publish)


# --- Display ---

panel = gridplot([[spec_map, spec]])

curdoc().add_root(column(marker_slider, energy_wavelength, panel,
    publish_button))

