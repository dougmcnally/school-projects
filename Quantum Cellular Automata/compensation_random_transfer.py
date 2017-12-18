import matplotlib 
from qutip import *
from math import *
from qca import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import csv
import cmath
import time
start = time.time()
inter_rate = numpy.linspace(0,.05,6)
comp = numpy.linspace(0,1,100) # compensation factor
N = 10
file_name = 'comp_avg_transfer.pdf'
num_states = 1000
fid = []
steps = N / 2
base = basis(2)
for i in range(N-2): base = tensor(base, basis(2))
sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

oper = ['m', 'zsum', 'z', 'm']
coeff = [-1./2, -3./4, -1./2, 1./2]
states = []
final_states = []

for i in range(num_states):
    # construct num_states random initial states
    alpha = random.random()
    beta = sqrt(1-alpha*alpha)
    phi = random.uniform(0,2*pi)
    psi0 = alpha*basis(2) + beta*cmath.exp(1j*phi)*basis(2,1)
    states.append(tensor(psi0,base))
    final_states.append(ket2dm(psi0).full())

for k in range(len(inter_rate)):
    print "Starting inter_rate #%i/%i"%(k+1,len(inter_rate))
    fid.append(numpy.zeros(len(comp)))
    expms = {'a':[],'b':[]}
    for i in range(len(oper)):
        if oper[i] != 'zsum':# include the interaction Hamiltonian in the control pulses (single bit gates)
            expms['a'].append((1.j * pi * coeff[i] * sigma[oper[i] + '_a'] - 1.j * pi * abs(coeff[i]) * inter_rate[k] * sigma['zsum_a']).expm())
            expms['b'].append((1.j * pi * coeff[i] * sigma[oper[i] + '_b'] - 1.j * pi * abs(coeff[i]) * inter_rate[k] * sigma['zsum_b']).expm())
        else:
            expms['a'].append(None)
            expms['b'].append(None)
    expms['a'][2] = expms['a'][2] * expms['a'][3]
    expms['b'][2] = expms['b'][2] * expms['b'][3]

    for ii in range(len(comp)):
        print "Starting comp #%i/%i"%(ii+1,len(comp))
        M_A = expms['a'][0] * (1.j * pi * coeff[1] * (1 - comp[ii]) * sigma['zsum_a']).expm() * expms['a'][2]
        M_B = expms['b'][0] * (1.j * pi * coeff[1] * (1 - comp[ii]) * sigma['zsum_b']).expm() * expms['b'][2]
        M = M_A * M_B
        fid_temp = 0
        update = M
        for i in range(2,steps+1):
            update = M * update
            if i == steps: update = sigma['z'][-1] * update
        for state in range(num_states):
            fid_temp += real(numpy.trace(numpy.dot((update * states[state]).ptrace(N-1).full(), final_states[state])))
        fid[k][ii] = fid_temp / num_states 

with open("comp_avg_transfer.csv","wb") as f:
    writer = csv.writer(f)
    writer.writerow(inter_rate)
    writer.writerow(comp)
    writer.writerows(fid)
    
colormap = plt.cm.rainbow
plt.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, len(inter_rate))])
for i in range(len(inter_rate)):
    plt.plot(comp,fid[i],label="$\gamma = %.2f$" % inter_rate[i])
plt.ylim(0,1)
plt.legend(ncol=3, loc='lower left', 
           columnspacing=.5, labelspacing=0.0,
           handletextpad=0.0, handlelength=1.2,
           fancybox=True, shadow=True, bbox_to_anchor=(0.075,0.8))
plt.xlabel("$C$",fontsize=18)
plt.ylabel("$F^{\hspace{.5}2}$",fontsize=18)
plt.savefig(file_name,bbox_inches='tight')
print "That took %.9f seconds!" % (time.time()-start)
