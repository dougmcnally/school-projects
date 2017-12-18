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
# construct the 3 necessary update rules
oper1 = ['m', 'zsum', 'z', 'm']
coeff1 = [-1./2, -3./4, -1./2, 1./2]
M_A1, M_B1 = build_M(sigma,oper1,coeff1)
M1 = M_A1 * M_B1

oper2 = ['m', 'zsum', 'z', 'm']
coeff2 = [-1./2, -7./8, -1./4, 1./2]
M_A2, M_B2 = build_M(sigma,oper2,coeff2)
M2 = M_A2 * M_B2

oper3 = ['m', 'z', 'y', 'zsum', 'z', 'y', 'zsum', 'z', 'z', 'y', 'zsum', 'y', 'z', 'x', 'z', 'y', 'zsum', 'z', 'm']
coeff3 = [-1./2,1./2,-1./2,-1./16,3./8,1./4,-1./4,3./2,-1./4,1./8,-3./4,1./4,1./4,1./8,1./2,1./4,-1./16,-1./8,1./2]
M_A3, M_B3 = build_M(sigma,oper3,coeff3)
M3 = M_A3 * M_B3


results = []
for i in range(N): results.append(numpy.zeros(k+2))
for j in range(N): results[j][0] = expect(sigma['+-'][j], psi0)

for i in range(1,k+2):
    if i == 1:
        psi0 = M_A3 * M_A2 * M_B3 * M_B2 * psi0
    elif i == k+1: # final update
        if N % 4 == 0: psi0 = (-1.j * pi / 4 * sigma['z'][0]).expm() * M_B1 * psi0
        else: psi0 = (-1.j * pi / 4 * sigma['z'][0]).expm() * M1 * psi0
    else:
        psi0 = M1 * psi0
    for j in range(N): results[j][i] = expect(sigma['+-'][j], psi0)


results = numpy.array(results).flatten()
qca_plot(N,k+2,results,labels=False,title="",file_name="entangle.png")
