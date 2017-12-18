from qutip import *
from math import *
from qca import *
import csv

trials = 2#100
max_g = 0.4
num_g = 8#0
g_vals = numpy.linspace(0,max_g,num_g)
Ns = [4,6]#,8,10]
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(num_g))

for N in Ns:
    steps = N / 2
    psi0 = (basis(2) + basis(2,1)).unit()
    for i in range(N-2): psi0 = tensor(psi0, basis(2))
    psi0 = tensor(psi0, (basis(2)-basis(2,1)).unit())
    sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

    oper = ['m', 'zsum', 'z', 'm']
    coeff_ = [-1./2, -3./4, -1./2, 1./2]
    M_A, M_B = build_M(sigma,oper,coeff_)
    M = M_A * M_B
    psi_final = Qobj(psi0)
    for i in range(steps):
        psi_final = M * psi_final 
        if i == steps-1: psi_final = sigma['z'][0] * sigma['z'][-1] * M_B * psi_final
    psi_final = psi_final.ptrace([0,N-1]).full()

    for ii in range(num_g):
        delta = g_vals[ii]
        fid = 0
        for j in range(trials):
            psi = Qobj(psi0)
            for i in range(1,steps + 2):
                for qb in range(N):
                    if random.random() <= delta:
                        if random.random() < 0.5: psi = sigma['x'][qb] * psi
                        else: psi = sigma['z'][qb] * psi
                if i <= steps: psi = M * psi
                else: psi = sigma['z'][0] * sigma['z'][-1] * M_B * psi
            fid += real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(),psi_final)))
        fid_average[int(N/2)-2][ii] = fid / trials
with open("flips_swap.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(g_vals)
    writer.writerows(fid_average)
fid_plot(g_vals,fid_average,len(Ns),xlabel="$\delta$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=False,scatter=False,file_name='flips_swap.png')
#title="Fidelity vs. Error Rate, 1D QCA State Swap [" + str(trials) + " trials]"
