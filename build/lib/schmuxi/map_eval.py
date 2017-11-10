import numpy as np
import matplotlib.pyplot as plt
import yaml
import bullshit

with open("spec_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

dimensions = cfg["map_paras"]["dimensions"]
background = cfg["map_paras"]["background"]
working_dir = cfg["general"]["working_dir"]
raw = np.loadtxt(working_dir + cfg["map_paras"]["file"])

data = raw[6:]

data3d = np.stack(np.vsplit(np.transpose(data)[1:],dimensions))-background


# print(np.shape(np.transpose(data)[1:]))

# print(np.shape(data3d))

z = np.sum(data3d,axis=2) 
z = z/np.max(z)
# print(np.shape(z))

# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_title('Intensity Map')

plt.axes([0.025,0.025,0.95,0.95])
plt.imshow(z, interpolation='nearest', cmap='hot', origin='lower',vmin=-0.2)
plt.colorbar(shrink=.92)

plt.xticks(())
plt.yticks(())
plt.show()
