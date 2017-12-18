from qutip import *
from math import *
from qca import *
import csv

trials = 5000
max_g = .4
num_g = 80
g_vals = numpy.linspace(0,max_g,num_g)
Ns = [4,6,8,10]
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(num_g))

for N in Ns:
    print "Starting N = %i" % N
    steps = N / 2
    psi0 = (basis(2) + basis(2,1)).unit()
    for i in range(N-1): psi0 = tensor(psi0, basis(2))
    sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

    oper = ['m', 'zsum', 'z', 'm']
    coeff_ = [-1./2, -3./4, -1./2, 1./2]
    M_A, M_B = build_M(sigma,oper,coeff_)
    M = M_A * M_B
    psi_final = ket2dm((basis(2)+basis(2,1)).unit()).full()

    for ii in range(num_g):
        if ii % 10 == 0: print "gamma #%i" % ii
        delta = g_vals[ii]
        fid = 0
        for j in range(trials):
            psi = Qobj(psi0)
            for i in range(1,steps + 1):
                for qb in range(N):
                    if random.random() <= delta:
                        if random.random() < 0.5: psi = sigma['x'][qb] * psi
                        else: psi = sigma['z'][qb] * psi
                psi = M * psi
                if i == steps: psi = sigma['z'][-1] * psi
            fid += real(numpy.trace(numpy.dot(psi.ptrace(N-1).full(),psi_final)))
        fid_average[int(N/2)-2][ii] = fid / trials
with open("flips_transfer.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(g_vals)
    writer.writerows(fid_average)
fid_plot(g_vals,fid_average,len(Ns),xlabel="$\delta$",ylabels=Ns,limit="twostate",
         title="", lin_fit=False,scatter=False,file_name="flips_transfer.pdf",vline=0.05)
#title="Fidelity vs. Error Rate, 1D QCA State Transfer [" + str(trials) + " trials]"
