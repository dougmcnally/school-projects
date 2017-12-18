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
psi_final = ket2dm((basis(2)+basis(2,1)).unit()).full()
for k in range(len(Ns)):
    fid.append(numpy.zeros(len(inter_rate)))
    N = Ns[k]
    steps = N / 2
    psi0 = (basis(2) + basis(2,1)).unit()
    for i in range(N-1): psi0 = tensor(psi0, basis(2))
    sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

    oper = ['m', 'zsum', 'z', 'm']
    coeff = [-1./2, -3./4, -1./2, 1./2]

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

        for i in range(1,steps + 1):
            psi = M * psi 
            if i == steps: 
                psi = sigma['z'][-1] * psi
        fid[k][ii] = real(numpy.trace(numpy.dot(psi.ptrace(N-1).full(), psi_final)))
with open("interactions_transfer.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerows(fid)
fid_plot(inter_rate,fid,len(Ns),xlabel="$\gamma$",ylabels=Ns,limit="twostate",
         title="",lin_fit=False,log_p=False,file_name="interactions_transfer.png")
#title="Fidelity vs. Interaction Rate, 1D QCA State Transfer w/ Interaction Always On"
