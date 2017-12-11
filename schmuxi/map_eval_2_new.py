'''Interactive tool to evaluate spectral maps.'''
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

with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
dim_x = -1
dim_y = -1
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
working_file = cfg["map_paras"]["file"]
calibration_file = cfg["map_paras"]["calibration_file"]


def labview_map(working_file):
    raw = np.loadtxt(working_dir + working_file)
    data = raw[6:]
    data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background
    calibration = data[:,0]
    dim_x = dimensions
    dim_y = dimensions
    return(data3d, calibration, dim_x, dim_y)


def mat_map(working_file, reset_background=True):
    data = sio.loadmat(working_dir + working_file)
    data3d = data['spectra']
    print(np.shape(data3d))
    print("^- up here")
    dim_x = np.shape(data3d)[0]
    print(dim_x)
    dim_y = np.shape(data3d)[1]
    if reset_background == True:
        background = 0
    data3d -= background
    try:
        calibration = data['wlen_to_px']
    except:
        calibration_data = pd.read_csv(working_dir + calibration_file, '\t', header=None)
        calibration = np.array(list(calibration_data[0]))
    print("calibrated with mat")
    return(data3d, calibration, dim_x, dim_y)
print("-v down here")
if working_file[-4:] == ".txt":
    data3d, calibration, dim_x, dim_y = labview_map(working_file)
elif working_file[-4:] == ".mat":
    data3d, calibration, dim_x, dim_y = mat_map(working_file)
else:
    print("Nope. Your file is some serious bullshit. You will hear from me later.")
print("here " + str(dim_x))
#print(np.shape(np.transpose(data)[1:]))

print(np.shape(data3d))
x = np.repeat(range(dim_x),dim_x)
y = np.tile(range(dim_y),dim_y)
z = np.sum(data3d,axis=2)
z = z/np.max(z)
print(np.shape(z))

Session = Experiment()

# Default
x_spec = dim_x-1
y_spec = dim_y-1

x2=1239.8/calibration
y2=data3d[x_spec,y_spec,:]

Session.convert_to_energy = False

TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

spec_map = figure(width=500, height=500, x_range=(0,dimensions), y_range=(0,dimensions), tools=TOOLS)
spec = figure(width=500, height = 500, tools=TOOLS)
print(np.shape(z))
print(dim_x + dim_y)
z = np.reshape(z,dim_x*dim_y)
colors = ["#%02x%02x%02x" % (int(r), int(r), int(r/2)) for r in
        np.around(255*z)]

spec_map.scatter(x, y, marker="square", size=7.5, fill_color=colors,
        line_color=None, selection_fill_color="red", nonselection_fill_alpha=0.8,
        nonselection_fill_color="fill_color")
#p.image(image=[z], x=0, y=0, dw=dimensions, dh=dimensions, palette="Inferno256")

r = spec.line(x=[],y=[], line_color="red")
marker = spec.line(x=[0,0],y=[0,10], line_color="green")
ds = r.data_source
ds2 = marker.data_source


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


marker_slider = Slider(start=0, end=1, value=0.5,
        step=0.002,
        title="Marker")


def adjust_marker(attr, old, new):
    '''adjust the position of the marker'''
    new_data = dict()
    new_data["x"] = [min(x2)+marker_slider.value*(max(x2)-min(x2)), min(x2)+marker_slider.value*(max(x2)-min(x2))]
    new_data["y"] = [0,max(ds.data["y"])]
    ds2.data = new_data


def publish():
    '''publishes the currently displayed spectrum, using spec_evaluation.py'''
    # Bad things happen here. Fix!
    publish_x = ds.data["x"]
    publish_y = ds.data["y"]
    publish_data = pd.DataFrame({'index': publish_x, 'values': publish_y})
    spectrum = Session.adjust_spectrum(publish_data, 
                                       background=False,
                                       overwrite_exposure=True,
                                       overwrite_rescaling=True)
    plot = Session.plot_spectrum(spectrum)
    Session.plot_to_png(plot, 'Fake_News.png')


energy_wavelength = Button(label="Fuck this up")
energy_wavelength.on_click(switch_calibration)
marker_slider.on_change('value',adjust_marker)
spec_map.on_event(Tap, display_spectrum)

publish_button = Button(label="Fool Referees")
publish_button.on_click(publish)
# output_file("spectralmap.html", title="Spectral Map")

panel = gridplot([[spec_map, spec]])
curdoc().add_root(column(marker_slider, energy_wavelength, panel,
    publish_button))

# output_server("hover")

# show(p)

