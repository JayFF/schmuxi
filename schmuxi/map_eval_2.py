'''Interactive tool to evaluate spectral maps.'''
import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import curdoc, gridplot, figure, show, output_file
from bokeh.layouts import column
from bokeh.models import Button, TapTool, Slider
from bokeh.events import Tap

with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
working_file = cfg["map_paras"]["file"]
raw = np.loadtxt(working_dir + working_file)

data = raw[6:]

data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background

calibration = data[:,0]

print(np.shape(np.transpose(data)[1:]))

print(np.shape(data3d))
x = np.repeat(range(dimensions),dimensions)
y = np.tile(range(dimensions),dimensions)
z = np.sum(data3d,axis=2)
z = z/np.max(z)
print(np.shape(z))

# Default
x_spec = 40
y_spec = 40

x2=1239.8/calibration
y2=data3d[x_spec,y_spec,:]


TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

spec_map = figure(width=500, height=500, x_range=(0,dimensions), y_range=(0,dimensions), tools=TOOLS)
spec = figure(width=500, height = 500, tools=TOOLS)

z = np.reshape(z,dimensions**2)
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

marker_slider = Slider(start=0, end=1, value=0.5,
        step=0.002,
        title="Marker")

def adjust_marker(attr, old, new):
    '''adjust the position of the marker'''
    new_data = dict()
    new_data["x"] = [min(x2)+marker_slider.value*(max(x2)-min(x2)), min(x2)+marker_slider.value*(max(x2)-min(x2))]
    new_data["y"] = [0,max(ds.data["y"])]
    ds2.data = new_data


energy_wavelength = Button(label="Fuck this up")
energy_wavelength.on_click(switch_calibration)
marker_slider.on_change('value',adjust_marker)
spec_map.on_event(Tap, display_spectrum)


# output_file("spectralmap.html", title="Spectral Map")

panel = gridplot([[spec_map, spec]])
curdoc().add_root(column(marker_slider, energy_wavelength, panel))

# output_server("hover")

# show(p)

