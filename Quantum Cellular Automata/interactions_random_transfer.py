from qutip import *
from math import *
from qca import *
import cmath
import csv

inter_rate = numpy.linspace(0,1,100)
num_states = 1000

# set the amount of pairwise interaction that
# will occur during the single qubit gates
# relative to the "duration" of the single bit gate
Ns = [4,6,8,10]
fid = []
#psi_final = ket2dm((basis(2)+basis(2,1)).unit()).full()
for k in range(len(Ns)):
    fid.append(numpy.zeros(len(inter_rate)))
    N = Ns[k]
    print "Starting N=%i" % N
    steps = N / 2
    sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

    oper = ['m', 'zsum', 'z', 'm']
    coeff = [-1./2, -3./4, -1./2, 1./2]

    for ii in range(len(inter_rate)):
        if ii % 10 == 0: print "Starting inter_rate #%i" % ii
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
        
        fid_temp = 0
        for state in range(num_states): # average over num_states randomly chosen initial states
            alpha = random.random()
            beta = sqrt(1-alpha*alpha)
            phi = random.uniform(0,2*pi)
            psi0 = alpha * basis(2) + beta * cmath.exp(1j*phi) * basis(2,1)
            psi = Qobj(psi0)
            for i in range(N-1): psi = tensor(psi, basis(2))

            for i in range(1,steps + 1):
                psi = M * psi 
                if i == steps: 
                    psi = sigma['z'][-1] * psi
            fid_temp += real(numpy.trace(numpy.dot(psi.ptrace(N-1).full(), ket2dm(psi0).full())))
        fid[k][ii] = fid_temp / num_states
with open("interactions_random_transfer.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerows(fid)
fid_plot(inter_rate,fid,len(Ns),xlabel="$\gamma$",ylabels=Ns,limit="twostate",
         title="",lin_fit=False,log_p=False,file_name="interactions_random_transfer.png")
#title="Fidelity vs. Interaction Rate, 1D QCA State Transfer w/ Interaction Always On"
