import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import curdoc, gridplot, figure, show, output_file
from bokeh.layouts import column
from bokeh.models import Button, TapTool
from bokeh.events import Tap
with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
raw = np.loadtxt(working_dir + cfg["map_paras"]["file"])

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

x_spec = 40
y_spec = 40

x2=calibration
y2=data3d[x_spec,y_spec,:]

#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.set_title('Intensity Map')
#hover = HoverTool(tooltips=[
#    ("index", "$index"),
#    ("(x,y)", "$x, $y"),
#])

TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave"

spec_map = figure(width=500, height=500, x_range=(0,dimensions), y_range=(0,dimensions), tools=TOOLS)
spec = figure(width=500, height = 500, tools=TOOLS)

z = np.reshape(z,dimensions**2)
colors = ["#%02x%02x%02x" % (int(r), int(r), int(r/2)) for r in
        np.around(255*z)]

spec_map.scatter(x, y, marker="square", size=7.5, fill_color=colors,
        line_color=None, nonselection_fill_alpha=0.8,
        nonselection_fill_color="fill_color")
#p.image(image=[z], x=0, y=0, dw=dimensions, dh=dimensions, palette="Inferno256")

r = spec.line(x=[],y=[], line_color="red")

ds = r.data_source


def callback(event):
    new_data = dict()
    new_data["x"] = calibration
    new_data["y"] = data3d[int(np.round(event.x)),int(np.round(event.y)),:]
    ds.data = new_data

button = Button(label="Fuck this up")
#taptool = TapTool()
spec_map.on_event(Tap, callback)


# output_file("spectralmap.html", title="Spectral Map")

p = gridplot([[spec_map, spec]])
curdoc().add_root(column(button, p))

# output_server("hover")

# show(p)

