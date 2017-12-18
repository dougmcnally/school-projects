from qutip import *
from math import *
from qca import *

trials = 1000
max_g = .05
num_g = 10
g_vals = numpy.linspace(0,max_g,num_g)
Ns = [4,6,8,10]
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(num_g))

for N in Ns:
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

    if N % 4 == 0: last_update = (1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm()
    else: last_update = (-1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * M_B
    
    psi_final = Qobj(psi0) # compute the final state with no errors
    for i in range(k+1):
        if i < k: psi_final = M * psi_final # apply the update k times
        else: psi_final = last_update * psi_final # final update        

    for ii in range(num_g):
        delta = g_vals[ii]
        fid = 0
        for j in range(trials):
            psi = Qobj(psi0)
            for i in range(1,k+2):
                for qb in range(N):
                    if random.random() <= delta:
                        if random.random() < 0.5: psi = sigma['x'][qb] * psi
                        else: psi = sigma['z'][qb] * psi
                if i < k + 1:
                    psi = M * psi
                else: # final update
                    psi = last_update * psi
            temp = (psi.dag() * psi_final).tr()
            fid += real(temp * conj(temp))
        fid_average[int(N/2)-2][ii] = fid / trials

fid_plot(g_vals,fid_average,len(Ns),xlabel="$\delta$ (Error Rate)",ylabels=Ns,limit="labels",
         title="Fidelity vs. Error Rate, 1D QCA GHZ State [" + str(trials) + " trials]",lin_fit=True,scatter=True)




