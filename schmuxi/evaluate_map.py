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

dimensions = cfg["map_paras"]["dimensions"]
dim_x = -1
dim_y = -1
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
working_file = cfg["map_paras"]["file"]
calibration_file = cfg["map_paras"]["calibration_file"]

# --- Function Declarations ---

def labview_map(working_file):
    raw = np.loadtxt(working_dir + working_file)
    data = raw[6:]
    data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background
    calibration = data[:,0]
    dim_x = dimensions
    dim_y = dimensions
    return(data3d, calibration, dim_x, dim_y)


def mat_map(working_file, reset_background=True):
    '''Loads a .mat file that describes a spectral mal'''
    data = sio.loadmat(working_dir + working_file)
    data3d = data['spectra']
    dim_x = np.shape(data3d)[0]
    dim_y = np.shape(data3d)[1]
    if reset_background == True:
        background = 0
    data3d -= background
    try:
        calibration = data['wlen_to_px']
    except:
        calibration_data = pd.read_csv(working_dir + calibration_file, '\t', header=None)
        calibration = np.array(list(calibration_data[0]))
    return(data3d, calibration, dim_x, dim_y)


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

if working_file[-4:] == ".txt":
    data3d, calibration, dim_x, dim_y = labview_map(working_file)
elif working_file[-4:] == ".mat":
    data3d, calibration, dim_x, dim_y = mat_map(working_file)
else:
    print("Nope. Your file is some serious bullshit. You will hear from me later.")

x = np.repeat(range(dim_x),dim_x)
y = np.tile(range(dim_y),dim_y)
z = np.sum(data3d,axis=2)
z = z/np.max(z)

Session = Experiment()
Session.convert_to_energy = False

x2=1239.8/calibration


# --- Data Visualization ---

TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

spec_map = figure(width=500, height=500, x_range=(-1,dim_x), y_range=(-1,dim_y), tools=TOOLS)
spec = figure(width=500, height = 500, tools=TOOLS)

z = np.reshape(z,dim_x*dim_y)

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

