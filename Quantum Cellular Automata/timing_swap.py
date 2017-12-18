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
sig = numpy.linspace(0,sigma_max,num_sigma)
count = 0
fid_average = list()
for i in range(len(Ns)): fid_average.append(numpy.zeros(len(sig)))

for N in Ns:
    print "Starting N =",N,"trial"
    sigma = init_operators(N, m_vec)

    # of the form M(1, u, u, u^2)
    oper = ['m', 'zsum', 'z', 'm']
    coeff_ = [-1./2, -3./4, -1./2, 1./2]
    M_A, M_B = build_M(sigma,oper,coeff_)
    M = M_A * M_B
    steps = N / 2

    # set the initial state for the first and last qubits
    # to some superposition states
    psi0 = (basis(2) + basis(2,1)).unit()
    for i in range(N-2): psi0 = tensor(psi0, basis(2))
    psi0 = tensor(psi0, (basis(2)+basis(2,1)).unit())
    
    # compute the errorless final state:
    psi_final = Qobj(psi0)
    for i in range(steps): psi_final = M * psi_final
    # last update
    psi_final = sigma['z'][0] * sigma['z'][-1] * M_B * psi_final
    psi_final = psi_final.ptrace([0,N-1]).full()

    for ii in range(len(sig)):
        # sig[ii] is the Gaussian width for this trial
        fid = numpy.zeros(trials)
        for j in range(trials):
            psi = Qobj(psi0) # copy the initial state to start fresh each trial
            for i in range(steps):
                # add some timing errors to the coefficients
                # sampled from a Gaussian distribution
                # NOTE: these need to be divided by pi since they 
                # will be multiplied by pi in the exponent
                coeff = numpy.zeros(len(coeff_))
                for jj in range(len(coeff)): coeff[jj] = coeff_[jj] + (random.gauss(mu,sig[ii]) / pi)
                # start with the unmodified coefficients and add a random error
                M_A, M_B = build_M(sigma,oper,coeff)
                psi = M_A * M_B * psi 
                if i == steps-1: # final update 
                    for jj in range(len(coeff)): coeff[jj] = coeff_[jj] + (random.gauss(mu,sig[ii]) / pi)
                    M_A, M_B = build_M(sigma,oper,coeff)
                    psi = sigma['z'][0] * sigma['z'][-1] * M_B * psi
            fid[j] = real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final))) # Tr( \rho_1 \rho_2 )
        fid_average[count][ii] = numpy.average(fid) # average over all the trials
    count += 1

with open("timing_swap1k.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(sig)
    writer.writerows(fid_average)
fid_plot(sig,fid_average,len(Ns),xlabel="$\sigma$",ylabels=Ns,limit="fourstate",
         title="",lin_fit=True,scatter=True,file_name="timing_swap1k.pdf",labelloc=0.043)
