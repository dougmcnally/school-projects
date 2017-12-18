from qutip import *
from math import *
from qca import *
N = 10
psi0 = basis(2)
if N % 4 == 0: # N = 4k
    k = N / 4
    for i in range(1,N):
        if i == N/2.:
            psi0 = tensor(psi0, (basis(2,1) + basis(2)).unit())
        else:
            psi0 = tensor(psi0, basis(2))
else: # N = 4k + 2
    k = (N-2)/4
    for i in range(1,N):
        if i == N/2. - 1:
            psi0 = tensor(psi0, (basis(2,1) + basis(2)).unit())
        else:
            psi0 = tensor(psi0, basis(2))
sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

oper = ['m', 'zsum', 'z', 'm']
coeff_ = [-1./2, -3./4, -1./2, 1./2]
M_A, M_B = build_M(sigma,oper,coeff_)
M = M_A * M_B

results = []
for i in range(N): results.append(numpy.zeros(k+2))
for j in range(N): results[j][0] = expect(sigma['+-'][j], psi0)

for i in range(1,k+2):
    if i < k + 1:
        psi0 = M * psi0
    else: # final update
        if N % 4 == 0: psi0 = (1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * psi0
        else: psi0 = (-1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * M_B * psi0
    for j in range(N): results[j][i] = expect(sigma['+-'][j], psi0)


results = numpy.array(results).flatten()
qca_plot(N,k+2,results,labels=False,title="",file_name="GHZ.png")
