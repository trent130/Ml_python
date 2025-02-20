import numpy as np

u = np.array([[1,2], [3,4]])
v = np.array([[0,5], [6,7]])

result = np.kron(u, v)

print(result)
