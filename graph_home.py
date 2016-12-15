import numpy as np
import pylab as plt

y = np.linspace(-10,60,500)
w=0.5
A = 10.

H = w*(1-y/A)**3

fig = plt.figure(facecolor='white')
ax = plt.gca()
plt.plot(y,H, color='black',linewidth=2.0)
plt.xlim(0, 40)
plt.ylim(-15, 5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.axhline(0, color='black')
plt.axvline(0, color='black')

plt.show()
