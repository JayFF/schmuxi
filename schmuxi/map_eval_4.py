import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.layouts import row, widgetbox

with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
raw = np.loadtxt(working_dir + cfg["map_paras"]["file"])

data = raw[6:]

data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background


print(np.shape(np.transpose(data)[1:]))

print(np.shape(data3d))
x = np.repeat(range(dimensions),dimensions)
y = np.tile(range(dimensions),dimensions)
z = np.sum(data3d,axis=2)
z = z/np.max(z)
print(np.shape(z))



#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.set_title('Intensity Map')
#hover = HoverTool(tooltips=[
#    ("index", "$index"),
#    ("(x,y)", "$x, $y"),
#])

TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave,box_select"

p = figure(x_range=(0,dimensions), y_range=(0,dimensions), tools=TOOLS)
p2 = figure()
z = np.reshape(z,dimensions**2)
colors = ["#%02x%02x%02x" % (int(r), int(r), int(r/2)) for r in np.around(255*z)]

p.scatter(x, y, marker="square", size=7.7, fill_color=colors, line_color=None)
#p.image(image=[z], x=0, y=0, dw=dimensions, dh=dimensions, palette="Inferno256")

output_file("spectralmap.html", title="Spectral Map")

show(p)

