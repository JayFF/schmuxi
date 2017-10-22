import numpy as np
import matplotlib.pyplot as plt
import yaml
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool
from bokeh._legacy_charts import HeatMap
with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
background = cfg["map_paras"]["background"]
raw = np.loadtxt(cfg["map_paras"]["file"])

data = raw[6:]

data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background

# this ist nothing but a shitty comment

print(np.shape(np.transpose(data)[1:]))

print(np.shape(data3d))

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

#p = figure(x_range=(0,dimensions), y_range=(0,dimensions))#, tools=[hover])

p = HeatMap(z, x=0, y=0, dw=dimensions, dh=dimensions, palette="Inferno256")

output_file("spectralmap.html", title="Spectral Map")

show(p)

