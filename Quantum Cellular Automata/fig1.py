from qutip import *
from math import *
from qca import *
N = 10
steps = N / 2
psi0 = (basis(2) + basis(2,1)).unit()
for i in range(N-1): psi0 = tensor(psi0, basis(2))
sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

oper = ['m', 'zsum', 'z', 'm']
coeff_ = [-1./2, -3./4, -1./2, 1./2]
M_A, M_B = build_M(sigma,oper,coeff_)
M = M_A * M_B

results = []
for i in range(N): results.append(numpy.zeros(steps + 1))
for j in range(N): results[j][0] = expect(sigma['+-'][j], psi0)

for i in range(1,steps + 1):
    psi0 = M * psi0 
    if i == steps: 
        psi0 = sigma['z'][-1] * psi0
    for j in range(N): results[j][i] = expect(sigma['+-'][j], psi0)


results = numpy.array(results).flatten()
qca_plot(N, steps+1,results,labels=False,title="",file_name="transfer.png")
