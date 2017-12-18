# Computational Physics Final Project
# Protein Folding
# - Optimized for faster runtime
# author Doug McNally

### IMPORTANT ###
# Running this program in IDLE may cause catastrophic failure when testing the plot_dynamic_temp()
# function.  Run this program manually from a directory, i.e. double click on the file icon when
# testing this function.  This is because of multiprocessing implemented to speed up results!

import numpy
import random
import math
import pylab

class AminoAcid:
    """
    A class to modle AminoAcid objects which stores thier
    type (represented by a number 1-20), there position in the chain,
    and any neighboring amino acids in the chain.
    """
    def __init__(self, kind, loc, left=None, right=None):
        self.kind, self.loc, self.left, self.right = kind, loc, left, right
    def __repr__(self):
        return str(self.kind) + ' at ' + str(self.loc)
    def __str__(self):
        return self.__repr__()

def display_protein(protein):
    """
    Shows a quasi-graphical representation of the protein.  Note that it is
    displayed such that the location of the protein is printed, not the type
    and therefore the covalent bonding can be discerned by the sequential
    numbering scheme - that is amino acids with number n are bonded to those
    with number n-1 and n+1 and this can be followed throughout the protein.
    """
    data, space, e = protein['data'], protein['space'], protein['e']
    for i, aa in enumerate(data):
        print str(i) + ': ' + str(aa)
    for r, rows in enumerate(space):
        for c, aa in enumerate(rows):
            if aa:
                index = data.index(aa)
                pad = (index < 10 and ' ') or ''
                print '[' + pad + str(index) + ']',
            else:
                print '[  ]',

def init(num):
    """
    Setup the initial structure of the protein.  This is done
    linearly along the horizontal axis of the grid.
    """
    data = []
    space = [[None for i in range(num)] for i in range(num)]
    for i in range(num):
        aa = AminoAcid(random.randint(1, 20), (0, i))
        data.append(aa)
        space[0][i] = aa
        # fill in the amino acids randomly (1-20, where
        # the number represents which type of amino acid)
    for i in range(num):
        if i:
            data[i].left = data[i-1]
        if num-1-i:
            data[i].right = data[i+1]
    return {'data':data, 'e':0, 'space':space}

def init_SAW(num, energies):
    """
    Create the initial structure of the protein by way of a
    Self Avoiding Random Walk (SAW).  This is suggested on page 395
    of Computational Physics.  Please note that for an input value of num
    greater than ~ 20 will almost certainly not work at short times (or at all)
    because of the nature of this algorithm!
    """
    count = 1
    bounds = num
    while count:
        loc = 0, 0
        num = bounds - 1
        space = [[None for i in range(bounds)] for i in range(bounds)]
        space[0][0] = aa = AminoAcid(random.randint(1, 20), loc)
        data = [aa]
        while num:
            num -= 1
            neighbors = nearest_neighbors(bounds, loc, adjacent = True)
            nr, nc = loc = neighbors[random.randint(0, len(neighbors) - 1)]
            if space[nr][nc]:
                break
            space[nr][nc] = bb = AminoAcid(random.randint(1, 20), loc)
            aa.right, bb.left = bb, aa
            aa, bb = bb, aa
            data.append(aa)
            if not num:
                return {'data':data, 'e':calc_energy(data, energies), 'space':space}

def attraction_energy():
    """
    Generate some hypothetical attraction energies between any
    two amino acids.  Therefore this must be a 20x20 matrix whose
    entries correspond to the attraction energy between the i-th
    and j-th amino acids.  Make this 21x21 to avoid 0 indexing.
    """
    energies = list()
    for i in range(21):
        energies.append(list())
        for j in range(21):
            energies[i].append(-2 * (random.random() + 1))
    # now make the matrix symmetric, because the i,j entry should
    # equal the j,i entry
    for i in range(len(energies)):
        for j in range(len(energies[i])):
            energies[i][j] = energies[j][i]
    return energies

detached = lambda a,b: a not in (b.left, b.right)

def calc_spot(protein, aa, energies):
    """
    In order to avoid the repeated calculation of the energy of the entire protein
    only the change in energy for a small selected region is considered because
    the rest should remain constant under such a so called "micro-step" structural
    transition.  This is one of several streamlined improvements to decrease run time
    on the method suggested in Computational Physics (pg. 394 - 404).
    """
    new_e = 0
    r, c = aa.loc
    data, space = protein['data'], protein['space']
    for nr, nc in nearest_neighbors(len(data), aa.loc, adjacent=True):
        bb = space[nr][nc]
        if bb and still_bonded(aa.loc, bb.loc) and detached(aa, bb):
            new_e += energies[aa.kind][bb.kind]
    return new_e

def calc_energy(aas, energies):
    """
    Calculates the current energy of the protein given the current
    spatial configuration (aas) and the attraction energies between
    amino acids of differen types (energies)
    """
    energy = 0
    for i in range(len(aas)):
        for j in range(i + 1, len(aas)):
            a, b = aas[i].loc, aas[j].loc
            if (still_bonded(a, b) and detached(aas[i], aas[j])):
                energy += energies[aas[i].kind][aas[j].kind]
    return energy
    
def fold_protein(protein, energies, T):
    """
    Choose a random protein and move it to a nearest neighbor site if
    available and the energy change is negative.  If energy change is positive,
    only allow if the Boltzmann factor is greater than a random number
    in [0,1).
    """
    data, space = protein['data'], protein['space']
    index = random.randint(0, len(data) -1)
    rndAA = data[index]
    # consider where the amino acid can move
    pot = nearest_neighbors(len(data), rndAA.loc)
    # now there is a list of places this amino acid
    # could theoretically move.  Must now choose 1 of these
    # check if it breaks a covalent bond, and then see if it
    # will occur    
    new_r, new_c = new_spot = pot[random.randint(0, len(pot)-1)] # tuple of the new location
    if space[new_r][new_c]:
        return False
    if rndAA.left and not still_bonded(new_spot, rndAA.left.loc):
        return False
    elif rndAA.right and not still_bonded(new_spot, rndAA.right.loc):
        return False
    old_e = calc_spot(protein, rndAA, energies)
    old_r, old_c = rndAA.loc
    space[old_r][old_c], space[new_r][new_c] = None, rndAA
    rndAA.loc = new_spot # left and right neightbors and type remain the same
    new_e = calc_spot(protein, rndAA, energies)    
    dE = new_e - old_e
    if (dE < 0) or (math.exp(-dE/T) > random.random()):
        protein['e'] += dE
        return True
    else:
        rndAA.loc = old_r, old_c
        space[old_r][old_c], space[new_r][new_c] = rndAA, None
        return False

def nearest_neighbors(bounds, loc, adjacent=False):
    """
    Determine all possible "nearest neighbor" locations
    on a square grid given a location (tuple) by adding
    unit movements in each of 8 possible directions and
    then see if they are allowed.  Only consider locations
    1 unit away if "adjacent" is True.
    """    
    unit_mov = (-1,-1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)
    if adjacent:
        unit_mov = (-1, 0), (0, 1), (1, 0), (0, -1)
    result = list()
    for r, c in unit_mov:
        nr, nc = loc[0] + r, loc[1] + c
        if nr >= 0 and nc >= 0 and nr < bounds and nc < bounds:
            result.append((nr, nc))
    return result
    
def still_bonded(loc1, loc2):
    """
    Check if two amino acids (loc1 and loc2 are tuples) are
    still bonded.  If not, this will return a number larger
    than 1 (F).  Iff the bond still exists, T will be returned.
    """
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]) == 1

def progress_report(progress_step):
    """ Give the current progress of the program as a percentage. """
    progress_report.progress = 0
    def _(new):
        if new - progress_report.progress >= progress_step:
            progress_report.progress = new
            print "Progress", str(progress_report.progress) + "%..."
            return new
    return _

def copy(protein):
    """ Create a deep copy of an amino acid list (i.e. protein). """
    num = len(protein['data'])
    data, space = [], [[None for i in range(num)] for i in range(num)]
    for i, aa in enumerate(protein['data']):
        r, c = aa.loc
        bb = AminoAcid(aa.kind, aa.loc)
        space[r][c] = bb
        data.append(bb)
        if i: bb.left, data[i-1].right = data[i-1], bb
    return {'e':protein['e'], 'data':data, 'space':space}

def calc_length(loc1, loc2):
    """
    Returns the current end to end length of a protein
    given its first and last amino acid locations.
    """
    return ((loc1[0]-loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5
    
def plot_folding(num, T, steps, energy=True, SAW=False, anneal=False):
    """
    Plots either the length or energy of the protein against time
    given the number of amino acids in the chain, the temperature (in
    units of Boltzmann's constant, the number of Monte Carlo time steps
    whether to plot energy or length, how to initilize the protein,
    and whether or not annealling will occur.
    """
    energies = attraction_energy() # The attractions between different amino acids
    if (not SAW): protein = init(num) # The amino acid positions
    else: protein = init_SAW(num, energies) # The amino acid can walk now
    display_protein(protein) # show the configuration at the start
    monte_carlo_steps = steps
    progress_step = 10
    x, y = [], []
    progress = progress_report(progress_step)
    for i in range(int(monte_carlo_steps)):
        if (anneal):
            if (i == int(steps/T)): T = 0.75 * T
            elif (i == 2*int(steps/T)): T = 0.5 * T
            elif (i == 3*int(steps/T)): T = 0.25 * T
        fold_protein(protein, energies, T)
        if energy:
            y.append(protein['e'])
        else:
            y.append(calc_length(protein['data'][0].loc, protein['data'][-1].loc))
        x.append(i)
        progress(round((i + 1)/monte_carlo_steps * 100))
    display_protein(protein) # show the configuration at the end
    pylab.plot(x, y)
    if energy:
        pylab.title("Protein Folding: Energy v. Time")
        pylab.ylabel("Energy (arb. units)")
    else:
        pylab.title("Protein Folding: End to End Length v. Time")
        pylab.ylabel("Length")
    pylab.xlabel("Time (Monte Carlo Steps)")
    pylab.show()

def create_process(T, protein, steps, energies):
    """
    Creates a subprocess to handle the averaging in
    plot_dynamic_temp() for one temperature.
    """
    z = []
    for i in range(int(steps)):
        fold_protein(protein, energies, T)
        #z.append(calc_length(protein['data'][0].loc, protein['data'][-1].loc))
        # the above line is to plot length instead of energy
        z.append(protein['e'])
    return T, sum(z)/len(z)
    
def plot_dynamic_temp(num, T, steps):
    """
    Calculates an average energy for the protein comprised of
    num AminoAcids over monte_carlo_steps data points for temperatures
    in the range 1 to T by 0.5 steps and plots this.  Ideally there
    is a distinct trend of higher energy -> higher (nearer to 0) energy.
    """
    from multiprocessing import Process, Pool
    monte_carlo_steps = steps
    base_protein = init(num) # The amino acid positions
    energies = attraction_energy()
    pool = Pool(None) # number of processes, cpu_count() by default
    x, y = [], []
    def get_result(result):
        T, average = result
        t = int(T*2-1)
        x.insert(t, T)
        y.insert(t, average)
        print T, average
    
    for t in range(20, 0, -1):
        if t == 1: continue
        pool.apply_async(create_process, args=(float(t)/2,
                                                copy(base_protein),
                                                monte_carlo_steps,
                                                energies),
                         callback = get_result)
    pool.close()
    pool.join()
    pylab.scatter(x, y)
    pylab.title("Protein Folding: Average Energy v. Temperature")
    pylab.ylabel("Energy (arb. units)")
    pylab.xlabel("Temperature (Boltzmann units)")
    pylab.show()

def plot_dynamic_temp_old(num, steps):
    """
    Calculates an average energy for the protein comprised of
    num AminoAcids over monte_carlo_steps data points for temperatures
    in the range 1 to 10 by 0.5 steps and plots this.  Ideally there
    is a distinct trend of higher energy -> higher (nearer to 0) energy.
    This should only be used if plot_dynamic_temp() will not work on
    your machine!
    """
    progress_step = 10
    monte_carlo_steps = steps
    base_protein = init(num) # The amino acid positions
    energies = attraction_energy() # The attractions between different amino acids
    x, y = [], []
    for t in range(20, 0, -1):
        protein = copy(base_protein)
        T = float(t)/2
        print 'T =', T
        z = []
        progress = progress_report(progress_step)
        for i in range(int(monte_carlo_steps)):
            fold_protein(protein, energies, T)
            z.append(protein['e'])
            progress(round((i + 1)/monte_carlo_steps * 100))
        total = sum(z)
        average = total / len(z)
        print 'average =', str(total) + "/" + str(len(z)) + "=" + str(average)
        y.append(average)
        x.append(T)
    pylab.scatter(x, y)
    pylab.title("Protein Folding: Energy v. Temperature")
    pylab.ylabel("Average Energy (arb. units)")
    pylab.xlabel("Temperature (Boltzmann units)")
    pylab.show()
    
if __name__ == '__main__':
    plot_folding(15, 1.0, 5e5, energy=True, SAW=False, anneal=False)
    #plot_dynamic_temp(15, 10, 10e5)
    #plot_dynamic_temp_old(15,5e5) # only use this if the test_with_processes() function does not work!

# In the above methods, each will produce a different plot modeling the behavior of a protein.  Select
# the apropriate on based on docstring descpritions (i.e. uncomment a method call above in the __main__ block,
# and in any method, a call to init() may be replaced with init_SAW() to intilize the protein with a
# Self Avoiding Walk (SAW) instead of a default straight line configuration.
