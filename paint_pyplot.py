#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt

# X = np.linspace(-np.pi, np.pi, 256, endpoint=True)
# C,S = np.cos(X), np.sin(X)

# plt.plot(X,C)
# plt.plot(X,S)

x = [i for i in range (10)]
list1 = [i**2 for i in range(10)]
list2 = [i*2 for i in range(10)]

plt.plot(x, list1, label='$x86$')
plt.plot(x, list2, 'r--',label='$arm$', linewidth=5)

plt.xlabel('Time')
plt.ylabel('Load')
plt.legend()
plt.show()
