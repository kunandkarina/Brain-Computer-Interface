import numpy as np

a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
a = a.reshape(-1, 1)
# print(a[0:5])
tmp = []
for i in range(5, len(a)):
    tmp.append(a[i-5:i])
tmp = np.array(tmp)
tmp = tmp.reshape(-1, 5)
print(tmp)