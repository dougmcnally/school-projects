# Quantum Trajectories Algorithm for implementation with QuTip
# Doug McNally and James Clemens

import numpy as np
from pylab import *
from scipy import *
from scipy.optimize import *
import copy
from multiprocessing import Pool
import multiprocessing
from itertools import repeat
import time
import cmath
from random import Random
from scipy.sparse import *
from qutip.odeoptions import Odeoptions
from qutip.odedata import Odedata

def mi_mcsolve(H,psi0,tlist,c_ops,e_ops,ntraj=500,args={},options=Odeoptions()):
    if psi0.type != 'ket':
        raise ValueError("psi0 must be a state vector")
    if type(ntraj) == int:
        ntraj = [ntraj]
    elif type(ntraj[0]) != int:
        raise ValueError("ntraj must either be an integer or a list of integers")
        
    num_eops = len(e_ops)
    num_cops = len(c_ops)
    # Just use mcsolve if there aren't any collapse or expect. operators
    if num_eops == num_cops == 0: raise ValueError("Must supply at least one expectation value operator.") 
	# should not ever meet this condition
	#return qutip.mcsolve(H, psi0, tlist, c_ops, e_ops, ntraj, args, options)
    elif num_cops == 0: ntraj = 1
    
    # Let's be sure we're not changing anything:
    H = copy.deepcopy(H)
    H = np.matrix(H.full())
    psi0 = copy.deepcopy(psi0)
    psi0 = psi0.full()
    tlist = copy.deepcopy(tlist)
    c_ops = copy.deepcopy(c_ops)
    for i in range(num_cops): c_ops[i] = np.matrix(c_ops[i].full())
    e_ops = copy.deepcopy(e_ops)
    eops_herm = [False for _ in range(num_eops)]
    for i in range(num_eops): 
        e_ops[i] = np.matrix(e_ops[i].full())
        eops_herm[i] = not any(abs(e_ops[i].getH()-e_ops[i])>1e-15) # check if each e_op is Hermetian
		
    # Construct the effective Hamiltonian
    Heff = H
    for cop in c_ops: Heff += -0.5j * np.dot(cop.getH(),cop)
    Heff = (-1j) * Heff
    # Find the eigenstates of the effective Hamiltonian
    la, v = np.linalg.eig(Heff)
    # Construct the similarity transformation matricies
    S = np.matrix(v)
    Sinv = np.linalg.inv(S)
    Heff_diag = np.dot(Sinv, np.dot(Heff, S)).round(10)
        
    for i in range(num_cops): c_ops[i] = np.dot(c_ops[i], S) # Multiply each Collapse Operator to the left by S
    
    psi0 = psi0 / np.linalg.norm(psi0)
    psi0_nb = np.dot(Sinv, psi0) # change basis for initial state vector

    for i in range(num_eops):
        e_ops[i] = np.dot(S.getH(), np.dot(e_ops[i], S)) # Change basis for the operator for which expectation values are requested
    
    if len(ntraj) > 1: 
        exp_vals = [list(np.zeros(len(tlist), dtype=(float if eops_herm[i] else complex)) for i in range(num_eops)) for _ in range(len(ntraj))]
        collapse_times_out = [list() for _ in range(len(ntraj))]
        which_op_out = [list() for _ in range(len(ntraj))]
    else: 
        exp_vals = list(np.zeros(len(tlist), dtype=(float if eops_herm[i] else complex)) for i in range(num_eops))
        collapse_times_out, which_op_out = list(), list()
    for _n in range(len(ntraj)): # ntraj can be passed in as a list
        print "Calculation Starting on", multiprocessing.cpu_count(), "CPUs"
        p = Pool()        
        def callback(r): # method to display progress
            callback.counter += 1
            if (round(100.0 * float(callback.counter) / callback.ntraj) >= 10 + round(100.0 * float(callback.last) / callback.ntraj)):
                print "Progress: %.0f%% (approx. %.2fs remaining)" % ((100.0 * float(callback.counter) / callback.ntraj),  ((time.time()-callback.start)/callback.counter * (callback.ntraj-callback.counter)))
                callback.last = callback.counter
        callback.last = 0
        callback.counter = 0
        callback.ntraj = ntraj[_n]
        callback.start = time.time()

        results = [r.get() for r in [p.apply_async(one_traj, (Heff_diag, S, Sinv, psi0_nb, tlist, e_ops, c_ops, num_eops, num_cops), {}, callback) for _ in range(ntraj[_n])]]
        p.close()
        p.join()
        # The following is a manipulation of the data resulting from the calculation
        # The goal is to output the results in an identical format as those from qutip.mcsolve()
        if len(ntraj) > 1:
            for i in range(ntraj[_n]):
                collapse_times_out[_n].append(results[i][1])
                which_op_out[_n].append(results[i][2])            
                for j in range(num_eops):
                    if eops_herm[j]: exp_vals[_n][j] += results[i][0][j].real
                    else: exp_vals[_n][j] += results[i][0][j]
            for i in range(num_eops): exp_vals[_n][i] = exp_vals[_n][i]/ntraj[_n]  
        else:
            for i in range(ntraj[_n]):
                collapse_times_out.append(results[i][1])
                which_op_out.append(results[i][2])            
                for j in range(num_eops):
                    if eops_herm[j]: exp_vals[j] += results[i][0][j].real
                    else: exp_vals[j] += results[i][0][j]
            for i in range(num_eops): exp_vals[i] = exp_vals[i]/ntraj[_n]
    output = Odedata()
    output.solver='mi_mcsolve'
    output.expect = exp_vals 
    output.times=tlist
    output.num_expect = num_eops
    output.num_collapse = num_cops
    output.ntraj = ntraj
    output.col_times = collapse_times_out
    output.col_which = which_op_out
    return output

def find_t(t, psi, S, Heff_diag, r):
    return -r + (np.linalg.norm(np.dot(np.dot(S, np.diag(np.exp(np.diag((Heff_diag * t))))), psi)))**2

def diag_expm(M_diag):
    return np.diag(np.exp(np.diag(M_diag)))

def mi_expect(Op, psi):
    return np.dot(psi.getH(), np.dot(Op, psi)).item(0) # this is a 1x1 matrix for some reason

def one_traj(Heff_diag, S, Sinv, psi0_nb, tlist, e_ops, c_ops, num_eops, num_cops):
    random = Random()
    exp_vals = list(np.zeros(len(tlist), dtype=complex) for i in range(num_eops))
    which_oper = list()
    collapse_times = list()
    for i in range(num_eops): exp_vals[i][0] += mi_expect(e_ops[i], psi0_nb) # Find the initial expectation values
    tmax = tlist[len(tlist)-1]
    prevjump = 0
    ind = 1
    try:
        nextjump = brentq(find_t, 0, tmax, xtol = 1e-6, args=(psi0_nb, S, Heff_diag, random.random()))
        collapse_times.append(nextjump) #dmm this has to be here, or there are times listed for the tmax case
    except:
        nextjump = tmax # the case that there is no zero on the interval [0, tmax]    
    flag = num_cops >= 1
    while ind < len(tlist):
        if nextjump < tlist[ind] and flag:            
            psi0_nb = np.dot(diag_expm(np.multiply(Heff_diag, (nextjump - prevjump))), psi0_nb)            
            if num_cops == 0: n_col = 0
            else: # choose which collapse operator acts on the state
                rand, tot, count, weight = random.random(), 0, -1, 0
                prob = np.zeros(num_cops)                
                for i in range(num_cops): 
                    prob[i] = (np.linalg.norm(np.dot(c_ops[i], psi0_nb)))**2
                    weight += prob[i]
                prob = prob/weight
                while rand > tot:
                    count += 1
                    tot += prob[count]                    
                n_col = count
            which_oper.append(n_col)
            # allow collapse operator to act on state vector at t = nextjump
            psi0_nb = np.dot(c_ops[n_col], psi0_nb) #np.dot(c_ops[n_col], psi0_nb)
            psi0_nb = psi0_nb / np.linalg.norm(psi0_nb)            
            psi0_nb = np.dot(Sinv, psi0_nb) # return to the basis where Heff is diagonal
            prevjump = nextjump
            try:
                nextjump += brentq(find_t, 0, tmax - prevjump, xtol = 1e-6, args=(psi0_nb, S, Heff_diag, random.random()))
                collapse_times.append(nextjump)
            except: flag = False
        # calculate expecatation values at t = tlist[ind]
        else:    
            psi0_nb = np.dot(diag_expm(np.multiply(Heff_diag, (tlist[ind] - prevjump))), psi0_nb)
            psi0_nb = np.dot(S, psi0_nb)
            psi0_nb = psi0_nb / np.linalg.norm(psi0_nb)
            psi0_nb = np.dot(Sinv, psi0_nb)
            for i in range(num_eops):
                exp_vals[i][ind] += mi_expect(e_ops[i], psi0_nb)
            prevjump = tlist[ind]
            ind += 1
    return exp_vals, collapse_times, which_oper
