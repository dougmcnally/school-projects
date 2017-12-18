from qutip import *
from math import *
from qca import *
import csv

inter_rate = numpy.linspace(0,1,200)

# set the amount of pairwise interaction that
# will occur during the single qubit gates
# relative to the "duration" of the single bit gate
Ns = [4,6,8,10]
fid = []

for kk in range(len(Ns)):
    fid.append(numpy.zeros(len(inter_rate)))
    N = Ns[kk]
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
    # compute the final sigmaz update z_final and store it to avoid redundant calculations
    z_final = (-1.j * pi / 4 * sigma['z'][0]).expm()
    
    for ii in range(len(inter_rate)):
        if ii % 10 == 0: print "Starting inter_rate #%i" % ii
        psi = Qobj(psi0) # copy the initial state
        M_A1, M_B1 = build_M(sigma,oper1,coeff1,gamma=inter_rate[ii])
        M1 = M_A1 * M_B1
        M_A2, M_B2 = build_M(sigma,oper2,coeff2,gamma=inter_rate[ii])
        M_A3, M_B3 = build_M(sigma,oper3,coeff3,gamma=inter_rate[ii])

        for i in range(1,k+2):
            if i == 1:
                psi = M_A3 * M_A2 * M_B3 * M_B2 * psi
            elif i == k+1: # final update
                if N % 4 == 0: psi = z_final * M_B1 * psi
                else: psi = z_final * M1 * psi
            else:
                psi = M1 * psi
        fid[kk][ii] = real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final)))
# write the data to a csv file:
with open("interactions_entangle.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerows(fid)
fid_plot(inter_rate,fid,len(Ns),xlabel="$\gamma$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=False,log_p=False,file_name="interactions_entangle.png")
#title="Fidelity vs. Interaction Rate, 1D QCA Entangled Pair w/ Interaction Always On"
