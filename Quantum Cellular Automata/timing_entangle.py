import matplotlib
matplotlib.use("Agg")
from qutip import *
from math import *
import random
import numpy
from qca import *
import csv

# consider timing errors in the form of over/under rotations
# during the applications of gate sequences, with errors
# sampled from a Gaussian distribution centered at mu, with
# width sigma

# simulation parameters:
sigma_max = .05     # max width of the Gaussian distro. to sample random # from
mu = 0.0            # mean of Gaussian (central value)
num_sigma = 10      # number of sigma values to sample (minimum sigma will be sigma / num_sigma) 
trials = 1000       # number of simulations for each sigma value
Ns = [4,6,8,10]     # numbers of qubits for which to run simulations
# end parameters

m_vec = (1 / sqrt(2), 0, 1 / sqrt(2)) # Bloch vector
sig = numpy.linspace(0,sigma_max, num_sigma)
count = 0
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(len(sig)))

for N in Ns:
    print "Starting N = %i trial" % N
    sigma = init_operators(N, m_vec)

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

    for ii in range(len(sig)):
        if ii % 2 == 0: print "Starting sig #%i" % ii
        # sig[ii] is the Gaussian width for this trial
        fid_temp = 0
        for j in range(trials):
            psi = Qobj(psi0) # copy the initial state to start fresh each trial
            for i in range(1,k+2):
                # add some timing errors to the coefficients
                # sampled from a Gaussian distribution
                # NOTE: these need to be divided by pi since they 
                # will be multiplied by pi in the exponent
                coeff1_ = numpy.zeros(len(coeff1))
                for jj in range(len(coeff1)): coeff1_[jj] = coeff1[jj] + (random.gauss(mu,sig[ii]) / pi)
                coeff2_ = numpy.zeros(len(coeff2))
                for jj in range(len(coeff2)): coeff2_[jj] = coeff2[jj] + (random.gauss(mu,sig[ii]) / pi)
                coeff3_ = numpy.zeros(len(coeff3))
                for jj in range(len(coeff3)): coeff3_[jj] = coeff3[jj] + (random.gauss(mu,sig[ii]) / pi)
                # start with the unmodified coefficients and add a random error
                M_A1, M_B1 = build_M(sigma,oper1,coeff1_)
                M_A2, M_B2 = build_M(sigma,oper2,coeff2_)
                M_A3, M_B3 = build_M(sigma,oper3,coeff3_)
                
                if i == 1: # first update
                    psi = M_A3 *  M_A2 * M_B3 * M_B2 * psi
                elif i == k+1: # final update
                    if N % 4 == 0: psi = (-1.j * ((pi / 4)+random.gauss(mu,sig[ii])) * sigma['z'][0]).expm() * M_B1 * psi
                    else: psi = (-1.j * ((pi / 4)+random.gauss(mu,sig[ii])) * sigma['z'][0]).expm() * M_A1 * M_B1 * psi
                else: # intermediate updates
                    psi = M_A1 * M_B1 * psi
            fid_temp += real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final)))
        fid_average[count][ii] = fid_temp / trials # average over all the trials
    count += 1
# write the data to a csv file:
with open("timing_entangle1k.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(sig)
    writer.writerows(fid_average)
fid_plot(sig,fid_average,len(Ns),xlabel="$\sigma$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=True,scatter=True,log_p=False,file_name="timing_entangle1k.pdf",labelloc=0.043)
#fid_plot(sig,fid_average,len(Ns),xlabel="$\sigma$",ylabels=Ns,limit="labels",
#         title="Fidelity vs. Error Rate, 1D QCA GHZ State [" + str(trials) + " trials]",lin_fit=True)
