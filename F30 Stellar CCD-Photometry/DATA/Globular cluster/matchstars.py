import itertools
import numpy as np
import _config_matchstars as _cfg

# list of files defined in _config_matchstars.py
filenames = [_cfg.lst_psffit_V, _cfg.lst_psffit_I]

# zeropoints defined in _config_matchstars.py
zero_V = _cfg.zero_V
zero_I = _cfg.zero_I

list_V, list_I, list_matched = ([] for i in range(3))
str_matched = ""

for f, lst in zip(filenames, [list_V, list_I]):
    with open(f) as f:
        # read in only every second line of the file
        for line in itertools.islice(f, None, None, 2):
            lst.append(line)
            
data_V = np.loadtxt(list_V, usecols=(0,1,2), unpack=True)
data_I = np.loadtxt(list_I, usecols=(0,1,2), unpack=True)

length = len(data_V[0])

for idx, (x_V, y_V, counts_V) in enumerate(zip(data_V[0], data_V[1], data_V[2])):
    if (idx % 500) == 0:
        print 'matching stars {:.2%} complete'.format(float(idx)/length)
    for x_I, y_I, counts_I in zip(data_I[0], data_I[1], data_I[2]):
        if abs(x_V - x_I) <= 1:
            if abs(y_V - y_I) <= 1:
                flux_V = zero_V - 2.5*np.log10(counts_V)
                flux_I = zero_I - 2.5*np.log10(counts_I)
                row = ('{:10.2f}'.format(x_V),
                       '{:10.2f}'.format(y_V),
                       '{:10.2f}'.format(counts_V),
                       '{:10.2f}'.format(counts_I),
                       '{:10.3f}'.format(flux_V),
                       '{:10.3f}'.format(flux_I))
                list_matched.append(row)
                
print 'matching stars 100% complete'

sep = ' '  # seperator for the join method
with open('stars_combined.txt', 'w') as f:
    for item in list_matched:
        f.write('{}\n'.format(sep.join(item)))
        
print 'resulting matched list saved in stars_combined.txt'