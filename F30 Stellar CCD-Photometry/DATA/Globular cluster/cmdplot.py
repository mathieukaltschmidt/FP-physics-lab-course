import matplotlib
matplotlib.use("Qt4Agg")
import numpy as np
import matplotlib.pyplot as plt
import ezpadova as ezp
import _config_cmdplot as _cfg
reload(_cfg)
import _config_cmdplot as _cfg

data = np.loadtxt(_cfg.lst_match, usecols=(4,5), unpack=True)
V = data[0]
I = data[1]

get_iso = lambda x, y: ezp.cmd.get_one_isochrone(x, y, phot='acs_wfc') 

#print(r.keys())
vk = 'F555W'
ik = 'F814W'

for key in _cfg.dct_iso.keys():
    Age = _cfg.dct_iso[key]["Age"]
    if Age >= 1e9:
        Age_str = '{:.1f} Gyr'.format(float(Age)/1e9)
    else:
        Age_str = '{:.1f} Myr'.format(float(Age)/1e6)
    Z = _cfg.dct_iso[key]["Z"]
    color = _cfg.dct_iso[key]["color"]
    iso = get_iso(Age, Z)
    plt.plot(iso[vk] - iso[ik], iso[vk] + _cfg.shift, color=color,
             label='Age={a}, Z={b}'.format(
                 a=Age_str,
                 b=float(Z))
            )
    
plt.scatter(V-I, V, s=0.05, color='black')
plt.gca().invert_yaxis()
plt.xlim(-0.3, 2)
plt.ylim(27.5, 16)
plt.legend()
plt.xlabel('V-I')
plt.ylabel('V')
#plt.title('Colour Magnitude Diagram BS90')
plt.savefig('CMD.png')
plt.show()
