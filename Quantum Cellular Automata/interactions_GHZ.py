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
for kk in range(len(Ns)):
    fid.append(numpy.zeros(len(inter_rate)))
    N = Ns[kk]
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
    coeff = [-1./2, -3./4, -1./2, 1./2]

    M_A, M_B = build_M(sigma,oper,coeff)
    M = M_A * M_B
    psi_final = Qobj(psi0)

    for i in range(1,k+2):
        if i < k + 1:
            psi_final = M * psi_final
        else: # final update
            if N % 4 == 0: psi_final = (1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * psi_final
            else: psi_final = (-1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * M_B * psi_final


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

        for i in range(1,k+2):
            if i < k + 1:
                psi = M * psi
            else: # final update
                if N % 4 == 0:
                    psi = (1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * psi
                else: psi = (-1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * M_B * psi
        temp = (psi.dag() * psi_final).tr()
        fid[kk][ii] = real(temp * conj(temp))
# write the data to a csv file:
with open("interactions_GHZ.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerows(fid)

fid_plot(inter_rate,fid,len(Ns),xlabel="$\gamma$",ylabels=Ns,limit="labels",
         title="",lin_fit=False,log_p=False,file_name="interactions_GHZ.png")
#title="Fidelity vs. Interaction Rate, 1D QCA GHZ State w/ Interaction Always On"
