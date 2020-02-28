#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# data = pd.Series(np.random.rand(1000))
data = pd.DataFrame([1,2,4,8,16,25,36,49])

# data = pd.DataFrame(np.random.randn(1000, 3), columns=['A','B','D'])
# data = data.cumsum()

print (data.head())
data.plot()

plt.show()
