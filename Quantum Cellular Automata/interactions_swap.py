from qutip import *
from math import *
from qca import *
import csv

inter_rate = numpy.linspace(0,1,100)

# set the amount of pairwise interaction that
# will occur during the single qubit gates
# relative to the "duration" of the single bit gate
Ns = [4,6,8,10]
fid = []

for k in range(len(Ns)):
    fid.append(numpy.zeros(len(inter_rate)))
    N = Ns[k]
    steps = N / 2
    psi0 = (basis(2) + basis(2,1)).unit()
    for i in range(N-2): psi0 = tensor(psi0, basis(2))
    psi0 = tensor(psi0, (basis(2)-basis(2,1)).unit())
    sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

    oper = ['m', 'zsum', 'z', 'm']
    coeff = [-1./2, -3./4, -1./2, 1./2]

    M_A, M_B = build_M(sigma,oper,coeff)
    M = M_A * M_B
    psi_final = Qobj(psi0)
    for i in range(steps):
        psi_final = M * psi_final 
        if i == steps-1: psi_final = sigma['z'][0] * sigma['z'][-1] * M_B * psi_final
    psi_final = psi_final.ptrace([0,N-1]).full()

    for ii in range(len(inter_rate)):
        psi = Qobj(psi0) # copy the initial state
        
        M_A = (1.j * pi * coeff[0] * sigma[oper[0] + '_a'] - 1.j * pi * abs(coeff[0]) * inter_rate[ii] * sigma['zsum_a']).expm()    
        M_B = (1.j * pi * coeff[0] * sigma[oper[0] + '_b'] - 1.j * pi * abs(coeff[0]) * inter_rate[ii] * sigma['zsum_b']).expm()
        for i in range(1, len(oper)):
            if oper[i] != 'zsum': # include the interaction Hamiltonian in the control pulses (single bit gates)
                M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a'] - 1.j * pi * abs(coeff[i]) * inter_rate[ii] * sigma['zsum_a']).expm()
                M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b'] - 1.j * pi * abs(coeff[i]) * inter_rate[ii] * sigma['zsum_b']).expm()
            else:
                M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a']).expm()
                M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b']).expm()
            
        M = M_A * M_B

        for i in range(steps):
            psi = M * psi
            if i == steps-1:
                psi = sigma['z'][0] * sigma['z'][-1] * M_B * psi
        fid[k][ii] = (real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final))))
# write the data to a csv file:
with open("interactions_swap.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerows(fid)
fid_plot(inter_rate,fid,len(Ns),xlabel="$\gamma$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=False,log_p=False,file_name="interactions_swap.png")
#title="Fidelity vs. Interaction Rate, 1D QCA State Swap w/ Interaction Always On"
