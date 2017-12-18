# This module contains various utility functions for QCA simulations
from qutip import *
from math import *
import random
import numpy
import matplotlib.pyplot as plt
import copy

def qca_plot(N,steps,vals,xlabel="Space (Qubit #)",ylabel="Time (update #)",
             title="QCA Plot",labels=False,file_name=False):
    # Used to plot the results of a QCA simulation 
    x = list()
    for i in range(N):
            for j in range(steps): x.append(i)
    y = list(range(steps)) * N
    plt.scatter(x, y, c=vals, marker='s', s=400, cmap=plt.get_cmap("gray"), norm=matplotlib.colors.NoNorm())
    plt.xlabel(xlabel,fontsize=18)
    plt.ylabel(ylabel,fontsize=18)
    plt.title(title)
    plt.xticks(range(N))
    plt.yticks(range(steps))
    plt.grid(True)
    plt.ylim(ymax=steps)
    plt.gca().invert_yaxis()

    if labels:
        for label, xcor, ycor in zip(["%.2f" % i for i in vals], x, y):
            plt.annotate(
                label, 
                xy = (xcor, ycor), xytext = (-20, 20),
                textcoords = 'offset points', ha = 'right', va = 'bottom',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
    plt.tick_params(labelsize=18)
    if file_name: plt.savefig(file_name,bbox_inches="tight",dpi=600)
    else: plt.show()

def fid_plot(x,ys,num_plots,xlabel="Error Rate",ylabels=None,
             title="Fidelity vs. Error Rate",lin_fit=False,limit="labels",
             log_p=False, scatter=False,vline=False,file_name=False,labelloc=False):
    ys = copy.deepcopy(ys)
    # Used to generate fidelity plots
    f, b = plt.subplots(num_plots, sharex=True, sharey=True)
    for i in range(num_plots):
        b[i].set_ylabel("$F^{\hspace{.5}2}$",fontsize=16)
        if ylabels:
            if limit == "labels": b[i].axhline(y=(1./(2**ylabels[i])),linestyle='dashed',color="black")
            elif limit == "fourstate": b[i].axhline(y=(1./4.),linestyle='dashed',color="black")
            elif limit == False: pass
            else: b[i].axhline(y=1./2,linestyle='dashed',color="black")
            # the fidelity for two random states ~ 1/N where N is the number of components
            # this is what is plotted as a dashed line, and this should be the lower bound
            # for fidelity
        if vline: b[i].axvline(x=vline,ymin=0,ymax=1.1,linestyle=':',color='red')
        b[i].set_ylim(bottom=0.0)
        b[i].set_ylim(top=1.1)
        y = ys[i][:]
        if log_p: y = log(y)
        if scatter: b[i].scatter(x, y)
        else:
            if ylabels:
                if labelloc == False: labelloc = 0.35
                b[i].plot(x, y, color='black')
                b[i].text(labelloc,0.85,'$n=%i$' % ylabels[i],fontsize=18)
            else: b[i].plot(x, y, color='black')
        if lin_fit:
            fit = numpy.polyfit(x, y, 1)
            r_sq = numpy.corrcoef(x,y)[0,1]**2
            fit_fn = numpy.poly1d(fit)
            b[i].plot(x, fit_fn(x))
            b[i].text((x[-1]-x[0])/2.,1.1/2.,"Slope = " +
                      str(fit_fn(2)-fit_fn(1)) + "\n$R^2=$ "+str(r_sq),fontsize=12)
    b[-1].set_xlabel(xlabel,fontsize=20)
    b[0].set_title(title)

    f.subplots_adjust(hspace=0.15)
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    if not log_p: plt.xlim([0,x[-1]])
    if file_name: plt.savefig(file_name,bbox_inches="tight")
    else: plt.show()

def build_M(sigma,oper,coeff,gamma=False,C=False):
    # Construct an update sequence M for running a QCA simulation
    # returns M_A (update rule for A species), M_B (B species)
    if not gamma and not C:
        M_A = (1.j * pi * coeff[0] * sigma[oper[0] + '_a']).expm()
        for i in range(1, len(oper)): M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a']).expm()
        M_B = (1.j * pi * coeff[0] * sigma[oper[0] + '_b']).expm()
        for i in range(1, len(oper)): M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b']).expm()
        return M_A, M_B
    elif isinstance(gamma,float):
        # assumes first operator is not zsum
        M_A = (1.j * pi * coeff[0] * sigma[oper[0] + '_a'] - 1.j * pi * abs(coeff[0]) * gamma * sigma['zsum_a']).expm()    
        M_B = (1.j * pi * coeff[0] * sigma[oper[0] + '_b'] - 1.j * pi * abs(coeff[0]) * gamma * sigma['zsum_b']).expm()
        for i in range(1, len(oper)):
            if oper[i] != 'zsum': # include the interaction Hamiltonian in the control pulses (single bit gates)
                M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a'] - 1.j * pi * abs(coeff[i]) * gamma * sigma['zsum_a']).expm()
                M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b'] - 1.j * pi * abs(coeff[i]) * gamma * sigma['zsum_b']).expm()
            else:
                if C:
                    M_A = M_A * (1.j * pi * coeff[i] * (1 - C) * sigma[oper[i] + '_a']).expm()
                    M_B = M_B * (1.j * pi * coeff[i] * (1 - C) * sigma[oper[i] + '_b']).expm()
                else:
                    M_A = M_A * (1.j * pi * coeff[i] * sigma[oper[i] + '_a']).expm()
                    M_B = M_B * (1.j * pi * coeff[i] * sigma[oper[i] + '_b']).expm()
        return M_A, M_B
    else: raise ValueError("Gamma must be provided if C is provided")

def init_operators(N, m_vec):
    # N is the number of qubits that the operators will be acting on
    # m_vec is the Bloch vector, supplied as a tuple (x,y,z)

    sigma = {'x':list(), 'y':list(), 'z':list(), '+-':list(), 'm_a':None, 'm_b':None,
             'x_a':None, 'y_a':None, 'z_a':None, 'x_b':None, 'y_b':None, 'z_b':None,
             'zsum_a':None, 'zsum_b':None, 'zsum':None}
    # note the follow correspondence:
    # x_a(b)    -> even(odd) sigmax total
    # y_a(b)    -> even(odd) sigmay total
    # z_a(b)    -> even(odd) sigmaz total
    # m_a(b)    -> even(odd) sigma directed along the Bloch vector
    # zsum_a(b) -> even(odd) sum of sigmaz_j * sigmaz_j+1 for "U([t])" with B.C. included
    for i in range(N):
        if i == 0:
            sigma['x'].append(sigmax())
            sigma['y'].append(sigmay())
            sigma['z'].append(sigmaz())
            sigma['+-'].append(sigmap() * sigmam())
        else:
            sigma['x'].append(qeye(2))
            sigma['y'].append(qeye(2))
            sigma['z'].append(qeye(2))
            sigma['+-'].append(qeye(2))
        for j in range(1,N):
            if i == j:
                sigma['x'][i] = tensor(sigma['x'][i], sigmax())
                sigma['y'][i] = tensor(sigma['y'][i], sigmay())
                sigma['z'][i] = tensor(sigma['z'][i], sigmaz())
                sigma['+-'][i] = tensor(sigma['+-'][i], sigmap() * sigmam())
            else:
                sigma['x'][i] = tensor(sigma['x'][i], qeye(2))
                sigma['y'][i] = tensor(sigma['y'][i], qeye(2))
                sigma['z'][i] = tensor(sigma['z'][i], qeye(2))
                sigma['+-'][i] = tensor(sigma['+-'][i], qeye(2))
    # Collect the sums of the operators
    sigma['x_a'], sigma['y_a'], sigma['z_a'] = sigma['x'][0], sigma['y'][0], sigma['z'][0]
    sigma['x_b'], sigma['y_b'], sigma['z_b'] = sigma['x'][1], sigma['y'][1], sigma['z'][1]

    for i in range(2,N):
        if not i % 2:
            sigma['x_a'] += sigma['x'][i]
            sigma['y_a'] += sigma['y'][i]
            sigma['z_a'] += sigma['z'][i]
        else:
            sigma['x_b'] += sigma['x'][i]
            sigma['y_b'] += sigma['y'][i]
            sigma['z_b'] += sigma['z'][i]
            
    sigma['m_a'] = m_vec[0] * sigma['x_a'] + m_vec[1] * sigma['y_a'] + m_vec[2] * sigma['z_a']
    sigma['m_b'] = m_vec[0] * sigma['x_b'] + m_vec[1] * sigma['y_b'] + m_vec[2] * sigma['z_b']

    # Construct sum of sigmaz products for "U([t])"
    sigma['zsum'] =  0 * sigma['z'][0]
    for i in range(N-1): sigma['zsum'] += sigma['z'][i] * sigma['z'][i+1]
    sigma['zsum_a'] = sigma['zsum'] + sigma['z'][0]  # even B.C.
    sigma['zsum_b'] = sigma['zsum'] + sigma['z'][-1] # odd B.C.   
    # make these all the same to include both B.C. on every update

    return sigma

def mail(to="dougmmcnally@gmail.com",msg="Simulation Done!"):
    import smtplib

    SERVER = "localhost"

    FROM = "dougmmcnally@gmail.com"
    TO = [to] # must be a list

    SUBJECT = "QCA Simulation Finished!"

    TEXT = msg

    # Prepare actual message

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail

    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()
