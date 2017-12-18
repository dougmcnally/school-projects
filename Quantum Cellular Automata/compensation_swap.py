from qutip import *
from math import *
from qca import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

inter_rate = numpy.linspace(0,.05,6)
comp = numpy.linspace(0,1,100) # compensation factor

N = 4
fid = []
steps = N / 2
psi0 = (basis(2) + basis(2,1)).unit()
for i in range(N-2): psi0 = tensor(psi0, basis(2))
psi0 = tensor(psi0, (basis(2)-basis(2,1)).unit())
sigma = init_operators(N,(1 / sqrt(2), 0, 1 / sqrt(2)))

oper = ['m', 'zsum', 'z', 'm']
coeff = [-1./2, -3./4, -1./2, 1./2]

M_A, M_B = build_M(sigma,oper,coeff)
M = M_A * M_B
psi_final = Qobj(psi0)
for i in range(steps):
    psi_final = M * psi_final 
    if i == steps-1: psi_final = sigma['z'][0] * sigma['z'][-1] * M_B * psi_final
psi_final = psi_final.ptrace([0,N-1]).full()

for k in range(len(inter_rate)):
    fid.append(numpy.zeros(len(comp)))

    for ii in range(len(comp)):
        psi = Qobj(psi0) # copy the initial state
        
        M_A = (1.j * pi * coeff[0] * sigma[oper[0] + '_a'] - 1.j * pi * abs(coeff[0]) * inter_rate[k] * sigma['zsum_a']).expm()    
        M_B = (1.j * pi * coeff[0] * sigma[oper[0] + '_b'] - 1.j * pi * abs(coeff[0]) * inter_rate[k] * sigma['zsum_b']).expm()
        for i in range(1, len(oper)):
            if oper[i] != 'zsum': # include the interaction Hamiltonian in the control pulses (single bit gates)
                M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a'] - 1.j * pi * abs(coeff[i]) * inter_rate[k] * sigma['zsum_a']).expm()
                M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b'] - 1.j * pi * abs(coeff[i]) * inter_rate[k] * sigma['zsum_b']).expm()
            else:
                M_A = M_A * (1.j * pi * coeff[i] * (1 - comp[ii]) * sigma[oper[i] + '_a']).expm()
                M_B = M_B * (1.j * pi * coeff[i] * (1 - comp[ii]) * sigma[oper[i] + '_b']).expm()
            
        M = M_A * M_B

        for i in range(steps):
            psi = M * psi
            if i == steps-1:
                psi = sigma['z'][0] * sigma['z'][-1] * M_B * psi
        fid[k][ii] = (real(numpy.trace(numpy.dot(psi.ptrace([0,N-1]).full(), psi_final))))

colormap = plt.cm.rainbow
plt.gca().set_color_cycle([colormap(i) for i in numpy.linspace(0, 0.9, len(inter_rate))])
for i in range(len(inter_rate)):
    plt.plot(comp,fid[i],label="$\gamma = %.2f$" % inter_rate[i])

plt.legend(ncol=3, loc='lower left', 
           columnspacing=1.0, labelspacing=0.0,
           handletextpad=0.0, handlelength=1.5,
           fancybox=True, shadow=True)
plt.xlabel("Compensation")
plt.ylabel("Fidelity")
plt.title("Fidelity vs. Compensation, $N = %i$ qubits, State Swap" % N)
plt.show()

# plot C corresponding to max Fid. vs. Gamma
Cs = []
for i in range(len(inter_rate)):
    Cs.append(comp[numpy.argmax(fid[i])])
plt.scatter(inter_rate,Cs)
plt.xlabel("$\gamma$")
plt.ylabel("$C_{max}$")
plt.title("$C_{max}$ vs $\gamma$ ($N = %i$ qubits)" % N)
# Add a best fit line
fit = numpy.polyfit(inter_rate, Cs, 1)
r_sq = numpy.corrcoef(inter_rate,Cs)[0,1]**2
fit_fn = numpy.poly1d(fit)
plt.plot(inter_rate,fit_fn(inter_rate))
plt.text((inter_rate[-1]-inter_rate[0])/2.,0,"$Slope = %.3f$\n$R^2=%.4f$" % (fit_fn(2)-fit_fn(1), r_sq),fontsize=12)
plt.show()

