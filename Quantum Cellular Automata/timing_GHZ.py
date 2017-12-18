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
    
    # compute the errorless final state:
    psi_final = Qobj(psi0)
    for i in range(k): psi_final = M * psi_final
    # last update
    if N % 4 == 0: # N = 4k case
        psi_final = (1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * psi_final
    else: # N = 4k + 2 case
        psi_final = M_B * psi_final
        psi_final = (-1.j * (-1)**k * pi / 4 * sigma['z'][0]).expm() * psi_final

    for ii in range(len(sig)):
        # sig[ii] is the Gaussian width for this trial
        fid = numpy.zeros(trials)
        for j in range(trials):
            psi = Qobj(psi0) # copy the initial state to start fresh each trial
            for i in range(k):
                # add some timing errors to the coefficients
                # sampled from a Gaussian distribution
                # NOTE: these need to be divided by pi since they 
                # will be multiplied by pi in the exponent
                coeff = numpy.zeros(len(coeff_))
                for jj in range(len(coeff)): coeff[jj] = coeff_[jj] + (random.gauss(mu,sig[ii]) / pi)
                # start with the unmodified coefficients and add a random error
                M_A, M_B = build_M(sigma,oper,coeff)
                psi = M_A * M_B * psi # apply the update k times
                if i == k-1: # final update 
                    if N % 4 == 0: # N = 4k case
                        psi = (1.j * (-1)**k * ((pi / 4)+random.gauss(mu,sig[ii])) * sigma['z'][0]).expm() * psi
                    else: # N = 4k + 2 case
                        for jj in range(len(coeff)): coeff[jj] = coeff_[jj] + (random.gauss(mu,sig[ii]) / pi)
                        M_A, M_B = build_M(sigma,oper,coeff)
                        psi = M_B * psi
                        psi = (-1.j * (-1)**k * ((pi / 4)+random.gauss(mu,sig[ii])) * sigma['z'][0]).expm() * psi
            temp = (psi.dag() * psi_final).tr()
            fid[j] = real(temp * conj(temp)) # <psi_final|psi>
        fid_average[count][ii] = numpy.average(fid) # average over all the trials
    count += 1
with open("timing_GHZ1k.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(sig)
    writer.writerows(fid_average)
fid_plot(sig,fid_average,len(Ns),xlabel="$\sigma$",ylabels=Ns,limit="labels",
         title="",lin_fit=True,scatter=True,file_name="timing_GHZ1k.pdf",labelloc=0.043)
