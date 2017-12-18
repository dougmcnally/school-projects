from qutip import *
from math import *
from qca import *
import csv

trials = 1000
max_g = .05
num_g = 10
g_vals = numpy.linspace(0,max_g,num_g)
Ns = [4,6,8,10]
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(num_g))

for N in Ns:
    print "Starting N = %i" % N
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

    oper3 = ['m', 'z', 'y', 'zsum', 'z', 'y', 'zsum', 'z', 'z', 'y', 'zsum', 'y', 'z', 'x', 'z', 'y', 'zsum', 'z', 'm']
    coeff3 = [-1./2,1./2,-1./2,-1./16,3./8,1./4,-1./4,3./2,-1./4,1./8,-3./4,1./4,1./4,1./8,1./2,1./4,-1./16,-1./8,1./2]
    M_A3, M_B3 = build_M(sigma,oper3,coeff3)

    psi_final = Qobj(psi0)
    # compute the errorless final state, psi_final
    for i in range(1,k+2):
        if i == 1:
            psi_final = M_A3 * M_A2 * M_B3 * M_B2 * psi_final
        elif i == k+1: # final update
            if N % 4 == 0: psi_final = (-1.j * pi / 4 * sigma['z'][0]).expm() * M_B1 * psi_final
            else: psi_final = (-1.j * pi / 4 * sigma['z'][0]).expm() * M1 * psi_final
        else:
            psi_final = M1 * psi_final
    psi_final = psi_final.ptrace([0,N-1]).full()  

    for ii in range(num_g):
        if ii%2 == 0: print "delta #%i" % ii
        delta = g_vals[ii]
        fid = 0
        for j in range(trials):
            psi = Qobj(psi0)
            for i in range(1,k+2):
                for qb in range(N):
                    if random.random() <= delta:
                        if random.random() < 0.5: psi = sigma['x'][qb] * psi
                        else: psi = sigma['z'][qb] * psi
                if i == 1: # first update
                    psi = M_A3 *  M_A2 * M_B3 * M_B2 * psi
                elif i == k+1: # final update
                    if N % 4 == 0: psi = (-1.j * pi / 4 * sigma['z'][0]).expm() * M_B1 * psi
                    else: psi = (-1.j * pi / 4 * sigma['z'][0]).expm() * M_A1 * M_B1 * psi
                else: # intermediate updates
                    psi = M_A1 * M_B1 * psi
            fid += real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final)))
        fid_average[int(N/2)-2][ii] = fid / trials
# write the data to a csv file:
with open("flips_entangle.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(g_vals)
    writer.writerows(fid_average)
fid_plot(g_vals,fid_average,len(Ns),xlabel="$\delta$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=True,scatter=True,log_p=False,file_name="flips_entangle.png",labelloc=0.043)
#fid_plot(g_vals,fid_average,len(Ns),xlabel="$\delta$ (Error Rate)",ylabels=Ns,limit="labels",
#         title="Fidelity vs. Error Rate, 1D QCA GHZ State [" + str(trials) + " trials]",lin_fit=True,scatter=True)




