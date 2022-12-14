import os
import numpy as np #from numpy import *
from scipy.spatial.distance import cdist
from itertools import combinations,permutations
from copy import deepcopy
import random
import codecs,json
import re

# Generates the adjacency matrix based on UFF bond radii
# Inputs:       Elements: N-element List strings for each atom type
#               Geometry: Nx3 np.array holding the geometry of the molecule
#               File:  Optional. If Table_generator encounters a problem then it is often useful to have the name of the file the geometry came from printed. 
def Table_generator(Elements,Geometry,File=None,Radii_dict=False):
    module_path =  '/'.join(os.path.abspath(__file__).split('/')[:-1])
    # Initialize UFF bond radii (Rappe et al. JACS 1992)
    # NOTE: Units of angstroms 
    # NOTE: These radii neglect the bond-order and electronegativity corrections in the original paper. Where several values exist for the same atom, the largest was used. 
    Radii = {  'H':0.354, 'He':0.849,\
              'Li':1.336, 'Be':1.074,                                                                                                                          'B':0.838,  'C':0.757,  'N':0.700,  'O':0.658,  'F':0.668, 'Ne':0.920,\
              'Na':1.539, 'Mg':1.421,                                                                                                                         'Al':1.244, 'Si':1.117,  'P':1.117,  'S':1.064, 'Cl':1.044, 'Ar':1.032,\
               'K':1.953, 'Ca':1.761, 'Sc':1.513, 'Ti':1.412,  'V':1.402, 'Cr':1.345, 'Mn':1.382, 'Fe':1.335, 'Co':1.241, 'Ni':1.164, 'Cu':1.302, 'Zn':1.193, 'Ga':1.260, 'Ge':1.197, 'As':1.211, 'Se':1.190, 'Br':1.192, 'Kr':1.147,\
              'Rb':2.260, 'Sr':2.052,  'Y':1.698, 'Zr':1.564, 'Nb':1.473, 'Mo':1.484, 'Tc':1.322, 'Ru':1.478, 'Rh':1.332, 'Pd':1.338, 'Ag':1.386, 'Cd':1.403, 'In':1.459, 'Sn':1.398, 'Sb':1.407, 'Te':1.386,  'I':1.382, 'Xe':1.267,\
              'Cs':2.570, 'Ba':2.277, 'La':1.943, 'Hf':1.611, 'Ta':1.511,  'W':1.526, 'Re':1.372, 'Os':1.372, 'Ir':1.371, 'Pt':1.364, 'Au':1.262, 'Hg':1.340, 'Tl':1.518, 'Pb':1.459, 'Bi':1.512, 'Po':1.500, 'At':1.545, 'Rn':1.42,\
              'default' : 0.7 }

    # SAME AS ABOVE BUT WITH A SMALLER VALUE FOR THE Al RADIUS ( I think that it tends to predict a bond where none are expected
    Radii = {  'H':0.39, 'He':0.849,\
              'Li':1.336, 'Be':1.074,                                                                                                                          'B':0.838,  'C':0.757,  'N':0.700,  'O':0.658,  'F':0.668, 'Ne':0.920,\
              'Na':1.539, 'Mg':1.421,                                                                                                                         'Al':1.15,  'Si':1.050,  'P':1.117,  'S':1.064, 'Cl':1.044, 'Ar':1.032,\
               'K':1.953, 'Ca':1.761, 'Sc':1.513, 'Ti':1.412,  'V':1.402, 'Cr':1.345, 'Mn':1.382, 'Fe':1.335, 'Co':1.241, 'Ni':1.164, 'Cu':1.302, 'Zn':1.193, 'Ga':1.260, 'Ge':1.197, 'As':1.211, 'Se':1.190, 'Br':1.192, 'Kr':1.147,\
              'Rb':2.260, 'Sr':2.052,  'Y':1.698, 'Zr':1.564, 'Nb':1.473, 'Mo':1.484, 'Tc':1.322, 'Ru':1.478, 'Rh':1.332, 'Pd':1.338, 'Ag':1.386, 'Cd':1.403, 'In':1.459, 'Sn':1.398, 'Sb':1.407, 'Te':1.386,  'I':1.382, 'Xe':1.267,\
              'Cs':2.570, 'Ba':2.277, 'La':1.943, 'Hf':1.611, 'Ta':1.511,  'W':1.526, 'Re':1.372, 'Os':1.372, 'Ir':1.371, 'Pt':1.364, 'Au':1.262, 'Hg':1.340, 'Tl':1.518, 'Pb':1.459, 'Bi':1.512, 'Po':1.500, 'At':1.545, 'Rn':1.42,\
              'default' : 0.7 }

    # Use Radii json file in Lib folder if sepcified
    if Radii_dict == True:
      if os.path.isfile(module_path+'/Radii.json') is False:
         print("ERROR: {}/Radii.json doesn't exist, check for Radii.json file in the Library".format(module_path))
         quit()
      Radii = read_alljson(module_path+'/Radii.json')


    Max_Bonds = {  'H':2,    'He':1,\
                  'Li':None, 'Be':None,                                                                                                                'B':4,     'C':4,     'N':4,     'O':2,     'F':1,    'Ne':1,\
                  'Na':None, 'Mg':None,                                                                                                               'Al':4,    'Si':4,  'P':None,  'S':None, 'Cl':1,    'Ar':1,\
                   'K':None, 'Ca':None, 'Sc':None, 'Ti':None,  'V':None, 'Cr':None, 'Mn':None, 'Fe':None, 'Co':None, 'Ni':None, 'Cu':None, 'Zn':None, 'Ga':None, 'Ge':None, 'As':None, 'Se':None, 'Br':1,    'Kr':None,\
                  'Rb':None, 'Sr':None,  'Y':None, 'Zr':None, 'Nb':None, 'Mo':None, 'Tc':None, 'Ru':None, 'Rh':None, 'Pd':None, 'Ag':None, 'Cd':None, 'In':None, 'Sn':None, 'Sb':None, 'Te':None,  'I':1,    'Xe':None,\
                  'Cs':None, 'Ba':None, 'La':None, 'Hf':None, 'Ta':None,  'W':None, 'Re':None, 'Os':None, 'Ir':None, 'Pt':None, 'Au':None, 'Hg':None, 'Tl':None, 'Pb':None, 'Bi':None, 'Po':None, 'At':None, 'Rn':None  }
                     
    # Scale factor is used for determining the bonding threshold. 1.2 is a heuristic that give some lattitude in defining bonds since the UFF radii correspond to equilibrium lengths. 
    scale_factor = 1.2

    # Print warning for uncoded elements.
    for i in Elements:
        if i not in Radii.keys():
            print( "ERROR in Table_generator: The geometry contains an element ({}) that the Table_generator function doesn't have bonding information for. This needs to be directly added to the Radii".format(i)+\
                  " dictionary before proceeding. Exiting...")
            quit()

    # Generate distance matrix holding atom-atom separations (only save upper right)
    Dist_Mat = np.triu(cdist(Geometry,Geometry))
    
    # Find plausible connections
    x_ind,y_ind = np.where( (Dist_Mat > 0.0) & (Dist_Mat < max([ Radii[i]**2.0 for i in Radii.keys() ])) )

    # Initialize Adjacency Matrix
    Adj_mat = np.zeros([len(Geometry),len(Geometry)])

    # Iterate over plausible connections and determine actual connections
    for count,i in enumerate(x_ind):
        
        # Assign connection if the ij separation is less than the UFF-sigma value times the scaling factor
        if Dist_Mat[i,y_ind[count]] < (Radii[Elements[i]]+Radii[Elements[y_ind[count]]])*scale_factor:            
            Adj_mat[i,y_ind[count]]=1
    
    # Hermitize Adj_mat
    Adj_mat=Adj_mat + Adj_mat.transpose()

    # Perform some simple checks on bonding to catch errors
    problem_dict = { i:0 for i in Radii.keys() }
    conditions = { "H":1, "C":4, "F":1, "Cl":1, "Br":1, "I":1, "O":2, "N":4, "B":4 }
    for count_i,i in enumerate(Adj_mat):

        if Max_Bonds[Elements[count_i]] is not None and sum(i) > Max_Bonds[Elements[count_i]]:
            problem_dict[Elements[count_i]] += 1
            cons = sorted([ (Dist_Mat[count_i,count_j],count_j) if count_j > count_i else (Dist_Mat[count_j,count_i],count_j) for count_j,j in enumerate(i) if j == 1 ])[::-1]
            while sum(Adj_mat[count_i]) > Max_Bonds[Elements[count_i]]:
                sep,idx = cons.pop(0)
                Adj_mat[count_i,idx] = 0
                Adj_mat[idx,count_i] = 0
#        if Elements[count_i] in conditions.keys():
#            if sum(i) > conditions[Elements[count_i]]:


    # Print warning messages for obviously suspicious bonding motifs.
    if sum( [ problem_dict[i] for i in problem_dict.keys() ] ) > 0:
        print( "Table Generation Warnings:")
        for i in sorted(problem_dict.keys()):
            if problem_dict[i] > 0:
                if File is None:
                    if i == "H": print( "WARNING in Table_generator: {} hydrogen(s) have more than one bond.".format(problem_dict[i]))
                    if i == "C": print( "WARNING in Table_generator: {} carbon(s) have more than four bonds.".format(problem_dict[i]))
                    if i == "Si": print( "WARNING in Table_generator: {} silicons(s) have more than four bonds.".format(problem_dict[i]))
                    if i == "F": print( "WARNING in Table_generator: {} fluorine(s) have more than one bond.".format(problem_dict[i]))
                    if i == "Cl": print( "WARNING in Table_generator: {} chlorine(s) have more than one bond.".format(problem_dict[i]))
                    if i == "Br": print( "WARNING in Table_generator: {} bromine(s) have more than one bond.".format(problem_dict[i]))
                    if i == "I": print( "WARNING in Table_generator: {} iodine(s) have more than one bond.".format(problem_dict[i]))
                    if i == "O": print( "WARNING in Table_generator: {} oxygen(s) have more than two bonds.".format(problem_dict[i]))
                    if i == "N": print( "WARNING in Table_generator: {} nitrogen(s) have more than four bonds.".format(problem_dict[i]))
                    if i == "B": print( "WARNING in Table_generator: {} bromine(s) have more than four bonds.".format(problem_dict[i]))
                else:
                    if i == "H": print( "WARNING in Table_generator: parsing {}, {} hydrogen(s) have more than one bond.".format(File,problem_dict[i]))
                    if i == "C": print( "WARNING in Table_generator: parsing {}, {} carbon(s) have more than four bonds.".format(File,problem_dict[i]))
                    if i == "Si": print( "WARNING in Table_generator: parsing {}, {} silicons(s) have more than four bonds.".format(File,problem_dict[i]))
                    if i == "F": print( "WARNING in Table_generator: parsing {}, {} fluorine(s) have more than one bond.".format(File,problem_dict[i]))
                    if i == "Cl": print( "WARNING in Table_generator: parsing {}, {} chlorine(s) have more than one bond.".format(File,problem_dict[i]))
                    if i == "Br": print( "WARNING in Table_generator: parsing {}, {} bromine(s) have more than one bond.".format(File,problem_dict[i]))
                    if i == "I": print( "WARNING in Table_generator: parsing {}, {} iodine(s) have more than one bond.".format(File,problem_dict[i]))
                    if i == "O": print( "WARNING in Table_generator: parsing {}, {} oxygen(s) have more than two bonds.".format(File,problem_dict[i]))
                    if i == "N": print( "WARNING in Table_generator: parsing {}, {} nitrogen(s) have more than four bonds.".format(File,problem_dict[i]))
                    if i == "B": print( "WARNING in Table_generator: parsing {}, {} bromine(s) have more than four bonds.".format(File,problem_dict[i]))
        print( "")

    return Adj_mat

# Canonicalizes the ordering of atoms in a geometry based on a hash function. Atoms that hash to equivalent values retain their relative order from the input geometry.
def canon_geo(elements,geo,adj_mat,atom_types):

    # Initialize mass_dict (used for identifying the dihedral among a coincident set that will be explicitly scanned)
    mass_dict = {'H':1.00794,'He':4.002602,'Li':6.941,'Be':9.012182,'B':10.811,'C':12.011,'N':14.00674,'O':15.9994,'F':18.9984032,'Ne':20.1797,\
                 'Na':22.989768,'Mg':24.3050,'Al':26.981539,'Si':28.0855,'P':30.973762,'S':32.066,'Cl':35.4527,'Ar':39.948,\
                 'K':39.0983,'Ca':40.078,'Sc':44.955910,'Ti':47.867,'V':50.9415,'Cr':51.9961,'Mn':54.938049,'Fe':55.845,'Co':58.933200,'Ni':58.6934,'Cu':63.546,'Zn':65.39,\
                 'Ga':69.723,'Ge':72.61,'As':74.92159,'Se':78.96,'Br':79.904,'Kr':83.80,\
                 'Rb':85.4678,'Sr':87.62,'Y':88.90585,'Zr':91.224,'Nb':92.90638,'Mo':95.94,'Tc':98.0,'Ru':101.07,'Rh':102.90550,'Pd':106.42,'Ag':107.8682,'Cd':112.411,\
                 'In':114.818,'Sn':118.710,'Sb':121.760,'Te':127.60,'I':126.90447,'Xe':131.29,\
                 'Cs':132.90545,'Ba':137.327,'La':138.9055,'Hf':178.49,'Ta':180.9479,'W':183.84,'Re':186.207,'Os':190.23,'Ir':192.217,'Pt':195.078,'Au':196.96655,'Hg':200.59,\
                 'Tl':204.3833,'Pb':207.2,'Bi':208.98038,'Po':209.0,'At':210.0,'Rn':222.0}

    # Canonicalize by sorting the elements based on hashing
    masses = [ mass_dict[i] for i in elements ]
    hash_list,atoms = [ list(j) for j in zip(*sorted([ (atom_hash(i,adj_mat,masses),i) for i in range(len(geo)) ],reverse=True)) ]

    # Update lists/np.arrays based on atoms
    geo   = geo[atoms]
    adj_mat    = adj_mat[atoms]
    adj_mat    = adj_mat[:,atoms]
    elements   = [ elements[i] for i in atoms ]
    atom_types = [ atom_types[i] for i in atoms ]
    
    return elements,geo,adj_mat,atom_types

# hashing function for canonicalizing geometries on the basis of their adjacency matrices and elements
# ind  : index of the atom being hashed
# A    : adjacency matrix
# M    : masses of the atoms in the molecule
# gens : depth of the search used for the hash   
def atom_hash(ind,A,M,alpha=100.0,beta=0.1,gens=10):    
    if gens <= 0:
        return rec_sum(ind,A,M,beta,gens=0)
    else:
        return alpha * sum(A[ind]) + rec_sum(ind,A,M,beta,gens)

# recursive function for summing up the masses at each generation of connections. 
def rec_sum(ind,A,M,beta,gens,avoid_list=[]):
    if gens != 0:
        tmp = M[ind]*beta
        new = [ count_j for count_j,j in enumerate(A[ind]) if j == 1 and count_j not in avoid_list ]
        if len(new) > 0:
            for i in new:
                tmp += rec_sum(i,A,M,beta*0.1,gens-1,avoid_list=avoid_list+[ind])
            return tmp
        else:
            return tmp
    else:
        return M[ind]*beta

# hashing function for canonicalizing geometries on the basis of their adjacency lists and elements
# ind  : index of the atom being hashed
# A    : adjacency list
# M    : masses of the atoms in the molecule
# gens : depth of the search used for the hash   
def atom_hash_list(ind,A,M,alpha=100.0,beta=0.1,gens=10):    
    if gens <= 0:
        return rec_sum_list(ind,A,M,beta,gens=0)        
    else:
        return alpha * len(A[ind]) + rec_sum_list(ind,A,M,beta,gens)

# recursive function for summing up the masses at each generation of connections. 
def rec_sum_list(ind,A,M,beta,gens,avoid_list=[]):
    if gens != 0:
        tmp = M[ind]*beta
        new = [ j for j in A[ind] if j not in avoid_list ]
        if len(new) > 0:
            for i in new:
                tmp += rec_sum_list(i,A,M,beta*0.1,gens-1,avoid_list=avoid_list+[ind])
            return tmp
        else:
            return tmp
    else:
        return M[ind]*beta

# Description: returns a canonicallized TAFFI bond. TAFFI bonds are written so that the lesser *atom_type* between 1 and 2 is first. 
# 
# inputs:      types: a list of taffi atom types defining the bond
#              ind:   a list of indices corresponding to the bond
#
# returns:     a canonically ordered bond (and list of indices if ind was supplied)
def canon_bond(types,ind=None):

    # consistency checks
    if len(types) != 2: 
        print( "ERROR in canon_bond: the supplied dihedral doesn't have two elements. Exiting...")
        quit()
    if ind != None and len(ind) != 2: 
        print( "ERROR in canon_bond: the iterable supplied to ind doesn't have two elements. Exiting...")
        quit()
        
    # bond types are written so that the lesser *atom_type* between 1 and 2 is first.
    if types[0] <= types[1]:
        if ind == None:
            return types
        else:
            return types,ind
    else:
        if ind == None:
            return types[::-1]
        else:
            return types[::-1],ind[::-1]

# Description: returns a canonicallized TAFFI angle. TAFFI angles are written so that the lesser *atom_type* between 1 and 3 is first. 
# 
# inputs:      types: a list of taffi atom types defining the angle
#              ind:   a list of indices corresponding to the angle
#
# returns:     a canonically ordered angle (and list of indices if ind was supplied)
def canon_angle(types,ind=None):

    # consistency checks
    if len(types) != 3: 
        print( "ERROR in canon_angle: the supplied dihedral doesn't have three elements. Exiting...")
        quit()
    if ind != None and len(ind) != 3: 
        print( "ERROR in canon_angle: the iterable supplied to ind doesn't have three elements. Exiting...")
        quit()
        
    # angle types are written so that the lesser *atom_type* between 1 and 3 is first.
    if types[0] <= types[2]:
        if ind == None:
            return types
        else:
            return types,ind
    else:
        if ind == None:
            return types[::-1]
        else:
            return types[::-1],ind[::-1]

# # Description: returns a canonicallized TAFFI dihedral. TAFFI dihedrals are written so that the lesser *atom_type* between 1 and 4 is first. 
# #              In the event that 1 and 4 are of the same type, then the lesser of 2 and 3 goes first. 
# #
# # inputs:      types: a list of taffi atom types defining the dihedral
# #              ind:   a list of indices corresponding to the dihedral
# #
# # returns:     a canonically ordered dihedral (and list of indices if ind was supplied)
# def canon_dihedral_old(types,ind=None):

#     # consistency checks
#     if len(types) != 4: 
#         print( "ERROR in canon_dihedral: the supplied dihedral doesn't have four elements. Exiting..."
#         quit()
#     if ind != None and len(ind) != 4: 
#         print( "ERROR in canon_dihedral: the iterable supplied to ind doesn't have four elements. Exiting..."
#         quit()
        
#     # dihedral types are written so that the lesser *atom_type* between 1 and 4 is first.
#     # In the event that 1 and 4 are of the same type, then the lesser of 2 and 3 goes first
#     if types[0] == types[3]:
#         if types[1] <= types[2]:
#             if ind == None:
#                 return types
#             else:
#                 return types,ind
#         else:
#             if ind == None:
#                 return types[::-1]
#             else:
#                 return types[::-1],ind[::-1]
#     elif types[0] < types[3]:
#         if ind == None:
#             return types
#         else:
#             return types,ind
#     else:
#         if ind == None:
#             return types[::-1]
#         else:
#             return types[::-1],ind[::-1]

# Description: returns a canonicallized TAFFI dihedral. TAFFI dihedrals are written so that the lesser *atom_type* between 1 and 4 is first. 
#              In the event that 1 and 4 are of the same type, then the lesser of 2 and 3 goes first. 
#
# inputs:      types: a list of taffi atom types defining the dihedral
#              ind:   a list of indices corresponding to the dihedral
#
# returns:     a canonically ordered dihedral (and list of indices if ind was supplied)
def canon_dihedral(types_0,ind=None):
    
    # consistency checks
    if len(types_0) < 4: 
        print( "ERROR in canon_dihedral: the supplied dihedral has less than four elements. Exiting...")
        quit()
    if ind != None and len(ind) != 4: 
        print( "ERROR in canon_dihedral: the iterable supplied to ind doesn't have four elements. Exiting...")
        quit()

    # Grab the types and style component (the fifth element if available)
    types = list(types_0[:4])
    if len(types_0) > 4:
        style = [types_0[4]]
    else:
        style = []

    # dihedral types are written so that the lesser *atom_type* between 1 and 4 is first.
    # In the event that 1 and 4 are of the same type, then the lesser of 2 and 3 goes first
    if types[0] == types[3]:
        if types[1] <= types[2]:
            if ind == None:
                return tuple(types+style)
            else:
                return tuple(types+style),ind
        else:
            if ind == None:
                return tuple(types[::-1]+style)
            else:
                return tuple(types[::-1]+style),ind[::-1]
    elif types[0] < types[3]:
        if ind == None:
            return tuple(types+style)
        else:
            return tuple(types+style),ind
    else:
        if ind == None:
            return tuple(types[::-1]+style)
        else:
            return tuple(types[::-1]+style),ind[::-1]

# Description: returns a canonicallized TAFFI improper. TAFFI impropers are written so that 
#              the three peripheral *atom_types* are written in increasing order.
#
# inputs:      types: a list of taffi atom types defining the improper
#              ind:   a list of indices corresponding to the improper
#
# returns:     a canonically ordered improper (and list of indices if ind was supplied)
def canon_improper(types,ind=None):

    # consistency checks
    if len(types) != 4: 
        print( "ERROR in canon_improper: the supplied improper doesn't have four elements. Exiting...")
        quit()
    if ind != None and len(ind) != 4: 
        print( "ERROR in canon_improper: the iterable supplied to ind doesn't have four elements. Exiting...")
        quit()
        
    # improper types are written so that the lesser *atom_type* between 1 and 4 is first.
    # In the event that 1 and 4 are of the same type, then the lesser of 2 and 3 goes first
    if ind == None:
        return tuple([types[0]]+sorted(types[1:]))
    else:
        tmp_types,tmp_ind = zip(*sorted(zip(types[1:],ind[1:])))
        return tuple([types[0]]+list(tmp_types[:])),tuple([ind[0]]+list(tmp_ind[:]))


# Helper function for Find_modes_tmp that removes duplicate modes
def remove_duplicate_modes(types,modes):
    a = [ tuple(sorted(_)) for _ in modes ]
    ind = [ a.index(_) for _ in set(a) ]
    return [ types[_] for _ in ind ],[ modes[_] for _ in ind ]

# A wrapper for the commands to parse the dihedrals from the adjacency matrix and geometry.
#           Atom_types isn't necessary here, this section of code just hasn't been cleaned up.
# Returns:  list of (dihedral_type,angle) tuples. 
def Find_modes(Adj_mat,Atom_types,Bond_mats,return_all=0,d1_opt=False):

    # Import here because of the dependency of id_type
    # Would be good to be able to call taffi_type() rather than id_types (not currently compatible)
    from id_types import id_types

    # Initialize lists of each instance and type of FF object.
    # instances are stored as tuples of the atoms involved 
    # (e.g., bonds between atoms 1 and 13 and 17 and 5 would be stored as [(1,13),(17,5)] 
    # Similarly, types are stored as tuples of atom types.
    Atom_types = [ next( j for j in i.split('link-') if j != '' ) for i in Atom_types ]    #  split('-link') call is necessary for handling fragment atoms
    Bonds = []
    Bond_types = []
    Angles = []
    Angle_types = []
    Dihedrals = []
    Dihedral_types = []
    One_fives = []
    VDW_types = []

    # Gen = 1 types are generated for angle and dihedral terms
    if d1_opt:
        g1_types = [] 
        for i in Atom_types:
            a,t = type_adjmat(i)
            g1_types += [id_types(t,a,gens=1)[0]]

    # Find bonds #
    for count_i,i in enumerate(Adj_mat):        
        Bonds += [ canon_bond((Atom_types[count_i],Atom_types[count_j]),(count_i,count_j)) for count_j,j in enumerate(i) if j == 1 and count_j > count_i ]
    Bond_types,Bonds = map(list,zip(*Bonds))

    # Remove -UA tag from Bond_types (united-atom has no meaning for bonds)
    Bond_types = [ (i[0].split('-UA')[0],i[1].split('-UA')[0]) for i in Bond_types ]

    # Find angles #
    # When d1_opt is supplied, the 1 and 3 atoms are typed based on depth=1 types
    for i in Bonds:        
        if d1_opt:
            Angles += [ canon_angle((g1_types[count_j],Atom_types[i[0]],g1_types[i[1]]),(count_j,i[0],i[1])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j != i[1] ]
            Angles += [ canon_angle((g1_types[i[0]],Atom_types[i[1]],g1_types[count_j]),(i[0],i[1],count_j)) for count_j,j in enumerate(Adj_mat[i[1]]) if j == 1 and count_j != i[0] ]
        else:
            Angles += [ canon_angle((Atom_types[count_j],Atom_types[i[0]],Atom_types[i[1]]),(count_j,i[0],i[1])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j != i[1] ]
            Angles += [ canon_angle((Atom_types[i[0]],Atom_types[i[1]],Atom_types[count_j]),(i[0],i[1],count_j)) for count_j,j in enumerate(Adj_mat[i[1]]) if j == 1 and count_j != i[0] ]

    Angle_types,Angles = remove_duplicate_modes(*map(list,zip(*Angles)))
    
    # Remove -UA tag from Angle_types (united-atom has no meaning for angles)
    Angle_types = [ (i[0].split('-UA')[0],i[1].split('-UA')[0],i[2].split('-UA')[0]) for i in Angle_types ]
        
    # Find dihedrals #
    # When d1_opt is supplied, the 1 and 4 atoms are typed based on depth=1 types
    for i in Angles:
        if d1_opt:
            Dihedrals += [ canon_dihedral((g1_types[count_j],Atom_types[i[0]],Atom_types[i[1]],g1_types[i[2]]),(count_j,i[0],i[1],i[2])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2]] ]
            Dihedrals += [ canon_dihedral((g1_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],g1_types[count_j]),(i[0],i[1],i[2],count_j)) for count_j,j in enumerate(Adj_mat[i[2]]) if j == 1 and count_j not in [i[0],i[1]] ]
        else:
            Dihedrals += [ canon_dihedral((Atom_types[count_j],Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]]),(count_j,i[0],i[1],i[2])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2]] ]
            Dihedrals += [ canon_dihedral((Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],Atom_types[count_j]),(i[0],i[1],i[2],count_j)) for count_j,j in enumerate(Adj_mat[i[2]]) if j == 1 and count_j not in [i[0],i[1]] ]
    if len(Dihedrals) != 0:
      Dihedral_types,Dihedrals = remove_duplicate_modes(*map(list,zip(*Dihedrals)))

    # Add Dihedral_type to dihedrals
    for count_i,i in enumerate(Dihedrals):
        if 2 in [ j[i[1],i[2]] for j in Bond_mats ]:
            Dihedral_types[count_i] = tuple(list(Dihedral_types[count_i]) + ["harmonic"])
        else:
            Dihedral_types[count_i] = tuple(list(Dihedral_types[count_i]) + ["opls"])                

    # Find 1-5s
    # NOTE: no effort is made to sort based on types because these are only used for coul and lj corrections
    for i in Dihedrals:
        
        # Find atoms attached to first atom of each dihedral
        One_fives += [ (count_j,i[0],i[1],i[2],i[3]) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2],i[3]] ]

        # Find atoms attached to the fourth atom of each dihedral
        One_fives += [ (i[0],i[1],i[2],i[3],count_j) for count_j,j in enumerate(Adj_mat[i[3]]) if j == 1 and count_j not in [i[0],i[1],i[2]] ]

    One_five_types = [ (Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],Atom_types[i[3]],Atom_types[i[4]]) for i in One_fives ]

    if return_all == 1: return Bonds,Angles,Dihedrals,One_fives,Bond_types,Angle_types,Dihedral_types,One_five_types
    else: return Bonds,Angles,Dihedrals,One_fives

# A wrapper for the commands to parse the dihedrals from the adjacency matrix and geometry.
#           Atom_types isn't necessary here, this section of code just hasn't been cleaned up.
# Returns:  list of (dihedral_type,angle) tuples. 
# XXX dihedrals failed for formaldehyde, raise an error for place charge for Drude
# but Drude's place charge only needs bonds, so this only return bonds, angles prevent place charge to fail
# XXX still need to look into why formaldehye failed
# return only bonds and angles, dihedral failed for formaldehyde
def Find_modes_baonly(Adj_mat,Atom_types,Bond_mats,return_all=0,d1_opt=False):

    # Import here because of the dependency of id_type
    # Would be good to be able to call taffi_type() rather than id_types (not currently compatible)
    from id_types import id_types

    # Initialize lists of each instance and type of FF object.
    # instances are stored as tuples of the atoms involved 
    # (e.g., bonds between atoms 1 and 13 and 17 and 5 would be stored as [(1,13),(17,5)] 
    # Similarly, types are stored as tuples of atom types.
    Atom_types = [ next( j for j in i.split('link-') if j != '' ) for i in Atom_types ]    #  split('-link') call is necessary for handling fragment atoms
    Bonds = []
    Bond_types = []
    Angles = []
    Angle_types = []
    Dihedrals = []
    Dihedral_types = []
    One_fives = []
    VDW_types = []

    # Gen = 1 types are generated for angle and dihedral terms
    if d1_opt:
        g1_types = [] 
        for i in Atom_types:
            a,t = type_adjmat(i)
            g1_types += [id_types(t,a,gens=1)[0]]

    # Find bonds #
    for count_i,i in enumerate(Adj_mat):        
        Bonds += [ canon_bond((Atom_types[count_i],Atom_types[count_j]),(count_i,count_j)) for count_j,j in enumerate(i) if j == 1 and count_j > count_i ]
    Bond_types,Bonds = map(list,zip(*Bonds))

    # Remove -UA tag from Bond_types (united-atom has no meaning for bonds)
    Bond_types = [ (i[0].split('-UA')[0],i[1].split('-UA')[0]) for i in Bond_types ]

    # Find angles #
    # When d1_opt is supplied, the 1 and 3 atoms are typed based on depth=1 types
    for i in Bonds:        
        if d1_opt:
            Angles += [ canon_angle((g1_types[count_j],Atom_types[i[0]],g1_types[i[1]]),(count_j,i[0],i[1])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j != i[1] ]
            Angles += [ canon_angle((g1_types[i[0]],Atom_types[i[1]],g1_types[count_j]),(i[0],i[1],count_j)) for count_j,j in enumerate(Adj_mat[i[1]]) if j == 1 and count_j != i[0] ]
        else:
            Angles += [ canon_angle((Atom_types[count_j],Atom_types[i[0]],Atom_types[i[1]]),(count_j,i[0],i[1])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j != i[1] ]
            Angles += [ canon_angle((Atom_types[i[0]],Atom_types[i[1]],Atom_types[count_j]),(i[0],i[1],count_j)) for count_j,j in enumerate(Adj_mat[i[1]]) if j == 1 and count_j != i[0] ]

    Angle_types,Angles = remove_duplicate_modes(*map(list,zip(*Angles)))
    
    # Remove -UA tag from Angle_types (united-atom has no meaning for angles)
    Angle_types = [ (i[0].split('-UA')[0],i[1].split('-UA')[0],i[2].split('-UA')[0]) for i in Angle_types ]
        
    # Find dihedrals #
    # When d1_opt is supplied, the 1 and 4 atoms are typed based on depth=1 types
    for i in Angles:
        if d1_opt:
            Dihedrals += [ canon_dihedral((g1_types[count_j],Atom_types[i[0]],Atom_types[i[1]],g1_types[i[2]]),(count_j,i[0],i[1],i[2])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2]] ]
            Dihedrals += [ canon_dihedral((g1_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],g1_types[count_j]),(i[0],i[1],i[2],count_j)) for count_j,j in enumerate(Adj_mat[i[2]]) if j == 1 and count_j not in [i[0],i[1]] ]
        else:
            Dihedrals += [ canon_dihedral((Atom_types[count_j],Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]]),(count_j,i[0],i[1],i[2])) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2]] ]
            Dihedrals += [ canon_dihedral((Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],Atom_types[count_j]),(i[0],i[1],i[2],count_j)) for count_j,j in enumerate(Adj_mat[i[2]]) if j == 1 and count_j not in [i[0],i[1]] ]
    #Dihedral_types,Dihedrals = remove_duplicate_modes(*map(list,zip(*Dihedrals)))

    # Add Dihedral_type to dihedrals
    #for count_i,i in enumerate(Dihedrals):
    #    if 2 in [ j[i[1],i[2]] for j in Bond_mats ]:
    #        Dihedral_types[count_i] = tuple(list(Dihedral_types[count_i]) + ["harmonic"])
    #    else:
    #        Dihedral_types[count_i] = tuple(list(Dihedral_types[count_i]) + ["opls"])                

    # Find 1-5s
    # NOTE: no effort is made to sort based on types because these are only used for coul and lj corrections
    #for i in Dihedrals:
    #    
        # Find atoms attached to first atom of each dihedral
    #    One_fives += [ (count_j,i[0],i[1],i[2],i[3]) for count_j,j in enumerate(Adj_mat[i[0]]) if j == 1 and count_j not in [i[1],i[2],i[3]] ]

        # Find atoms attached to the fourth atom of each dihedral
    #    One_fives += [ (i[0],i[1],i[2],i[3],count_j) for count_j,j in enumerate(Adj_mat[i[3]]) if j == 1 and count_j not in [i[0],i[1],i[2]] ]

    #One_five_types = [ (Atom_types[i[0]],Atom_types[i[1]],Atom_types[i[2]],Atom_types[i[3]],Atom_types[i[4]]) for i in One_fives ]
    if return_all == 1: return Bonds,Angles,Bond_types,Angle_types

    #if return_all == 1: return Bonds,Angles,Dihedrals,One_fives,Bond_types,Angle_types,Dihedral_types,One_five_types
    else: return Bonds,Angles,Dihedrals,One_fives
        

# Description: This is a simple implementation of the Dijkstra algorithm for 
#              finding the backbone of a polymer 
def Dijkstra(Adj_mat,start=0,end=-1):

    
    # Default to the last node in Adj_mat if end is unassigned or less than 0
    if end < 0:
        end = len(Adj_mat)+end

    # Remove terminal sites (sites with only a single length 2
    # self walk). Continue until all of the terminal structure 
    # has been removed from the topology.
    Adj_trimmed = np.copy(Adj_mat)

    # Initialize Distances, Previous, and Visited lists    
    Distances = np.array([100000]*(len(Adj_mat))) # Holds shortest distance to origin from each site
    Distances[start] = 0 # Sets the separation of the initial node from the initial node to zero
    Previous = np.array([-1]*len(Adj_mat)) # Holds the previous site on the short distance to origin
    Visited = [0]*len(Adj_mat) # Holds which sites have been visited

    # Initialize current site (i) and neighbors list
    i = start # current site
    neighbors = []

    # Iterate through sites. At each step find the shortest distance between all of hte 
    # current sites neighbors and the START. Update the shortest distances of all sites
    # and choose the next site to iterate on based on which has the shortest distance of
    # among the UNVISITED set of sites. Once the terminal site is identified the shortest
    # path has been found
    while( 0 in Visited):

        # If the current site is the terminal site, then the algorithm is finished
        if i == end:
            break

        # Add new neighbors to the list
        neighbors = [ count_j for count_j,j in enumerate(Adj_trimmed[i]) if j == 1 ]

        # Remove the current site from the list of unvisited
        Visited[i] = 1

        # Iterate over neighbors and update shortest paths
        for j in neighbors:

            # Update distances for current generation of connections
            if Distances[i] + Adj_trimmed[j,i] < Distances[j]:
                Distances[j] = Distances[i] + Adj_trimmed[j,i]
                Previous[j] = i

        # Find new site based on the minimum separation (only go to unvisited sites!)
        tmp = min([ j for count_j,j in enumerate(Distances) if Visited[count_j] == 0])
        i = [ count_j for count_j,j in enumerate(Distances) if j == tmp and Visited[count_j] == 0 ][0]

    # Find shortest path by iterating backwards
    # starting with the end site.
    Shortest_path = [end]
    i=end
    while( i != start):
        Shortest_path = Shortest_path + [Previous[i]]    
        i = Previous[i]

    # Reverse order of the list to go from start to finish
    Shortest_path = Shortest_path[::-1]
    return Shortest_path

# Return true if idx is a ring atom
def ring_atom(adj_mat,idx):

    # Find the atoms connected to atom idx
    connections = [ count_i for count_i,i in enumerate(adj_mat[idx]) if i == 1 ]

    # If there isn't at least two connections then there is no possibility that this is a ring atom
    if len(connections) < 2:
        return False

    # Loop through all unique pairs of atom indices connected to idx
    for i in combinations(connections,2):

        # If two atoms connected to atom idx have identical sets of connections then idx is a ring atom
        if return_connected(adj_mat,start=i[0],avoid=[idx]) == return_connected(adj_mat,start=i[1],avoid=[idx]):
            return True

    # If the fuction gets to this point then idx is not a ring atom
    return False

# Return the indices of ring systems that contain the atom atoms in idx
def return_ring(idx,adj_mat,atomtypes=None):

    # Only keep elements of idx that are ring atoms
    ring_idx = [ i for i in idx if ring_atom(adj_mat,i) is True ]

    # Iterate over the ring_idx list and append connected ring atoms to the list without backtracking
    for i in ring_idx:

        # Find the atoms connected to atom i
        ring_idx += [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and ring_atom(adj_mat,count_j) is True and count_j not in ring_idx  ]

    return ring_idx

# Return bool depending on if the atom is a nitro nitrogen atom
def is_nitro(i,adj_mat,elements):

    status = False
    if elements[i] not in ["N","n"]:
        return False
    O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ] 
    if len(O_ind) == 2:
        return True
    else:
        return False

# Return bool depending on if the atom is a sulfoxide sulfur atom
def is_sulfoxide(i,adj_mat,elements):

    status = False
    if elements[i] not in ["S","s"]:
        return False
    O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ] 
    C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["c","C"] ] 
    if len(O_ind) == 1 and len(C_ind) == 2:
        return True
    else:
        return False

# Return bool depending on if the atom is a sulfonyl sulfur atom
def is_sulfonyl(i,adj_mat,elements):

    status = False
    if elements[i] not in ["S","s"]:
        return False
    O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ] 
    C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["c","C"] ] 
    if len(O_ind) == 2 and len(C_ind) == 2:
        return True
    else:
        return False

# Return bool depending on if the atom is a phosphate phosphorus atom
def is_phosphate(i,adj_mat,elements):

    status = False
    if elements[i] not in ["P","p"]:
        return False
    O_ind      = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] ] 
    O_ind_term = [ j for j in O_ind if sum(adj_mat[j]) == 1 ]
    if len(O_ind) == 4 and sum(adj_mat[i]) == 4 and len(O_ind_term) > 0:
        return True
    else:
        return False

# Return bool depending on if the atom is a cyano nitrogen atom
def is_cyano(i,adj_mat,elements):

    status = False
    if elements[i] not in ["N","n"] or sum(adj_mat[i]) > 1:
        return False
    C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["c","C"] and sum(adj_mat[count_j]) == 2 ]
    if len(C_ind) == 1:
        return True
    else:
        return False

# Return bool depending on if the atom is a cyano nitrogen atom
def is_isocyano(i,adj_mat,elements):

    status = False
    if elements[i] not in ["N","n"] or sum(adj_mat[i]) > 1:
        return False
    C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["c","C"] and sum(adj_mat[count_j]) == 1 ]
    if len(C_ind) == 1:
        return True
    else:
        return False

# is function for fragments
# Return bool depending on if the atom is a sulfoxide sulfur atom
def is_frag_sulfoxide(i,adj_mat,elements):

    status = False
    if elements[i] not in ["S","s"]:
        return False
    O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1] 
    connect = sum(adj_mat[i])

    if len(O_ind) == 1 and int(connect) >= 2:
        return True
    else:
        return False

# Return bool depending on if the atom is a sulfonyl sulfur atom
def is_frag_sulfonyl(i,adj_mat,elements):

    status = False
    if elements[i] not in ["S","s"]:
        return False
    O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1] 
    connect = sum(adj_mat[i])

    if len(O_ind) == 2 and int(connect) >= 3:
        return True
    else:
        return False

# Returns a list with the number of electrons on each atom and a list with the number missing/surplus electrons on the atom
# 
# Inputs:  atomtypes:
#          adj_mat: 
#
# Returns: lone_electrons:
#          bonding_electrons:
#          core_electrons:
#
def check_lewis_old(atomtypes,adj_mat,q_tot=0,bonding_pref=None,return_pref=False,verbose=False):

    # Initialize the preferred lone electron dictionary the first time this function is called
    if not hasattr(check_lewis, "sat_dict"):

        check_lewis.lone_e = {      'h':0, 'he':2,\
                                   'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                                   'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                                    'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                                   'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                                   'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None  }

        # Initialize periodic table
        check_lewis.periodic = { "h": 1,  "he": 2,\
                                 "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                                 "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                                  "k":19, "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                                 "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                                 "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}

        # Initialize periodic table
        check_lewis.atomic_to_element = { check_lewis.periodic[i]:i for i in check_lewis.periodic.keys() }

        # Electronegativity ordering (for determining lewis structure)
    #     check_lews.en_order = [9,8,17,7,36,55,56,16,34,6,81,76,84,80,\
    #                            46,87,79,78,47,45,1,15,33,43,54,53,5,\
    #                            85,31,86,82,51,48,27,77,44,28,14,26,25,\
    #                            30,50,49,23,29,22,83,13,42,4,24,21,93,\
    #                            75,94,95,20,41,12,105,104,103,102,101,\
    #                            100,99,98,97,92,74,96,73,71,70,69,68,\
    #                            40,66,64,62,61,60,91,59,19,3,39,11,90,\
    #                            58,38,19,57,89,2,10,18,63,65,67,72,88]

    # Initalize elementa and atomic_number lists for use by the function
    elements = [ check_lewis.atomic_to_element[int(i.split("[")[1].split("]")[0])] for i in atomtypes ]
    atomic_number = [ int(i.split("[")[1].split("]")[0]) for i in atomtypes ]
    
    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(atomtypes),dtype="int")    
    bonding_electrons = np.zeros(len(atomtypes),dtype="int")    
    core_electrons    = np.zeros(len(atomtypes),dtype="int")
    valence           = np.zeros(len(atomtypes),dtype="int")
    bonding_target    = np.zeros(len(atomtypes),dtype="int")
    for count_i,i in enumerate(atomtypes):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = int(i.split('[')[1].split(']')[0])

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print( "ERROR in check_lewis: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot

        # Assign target number of bonds for this atom
        if count_i in [ j[0] for j in bonding_pref ]:
            bonding_target[count_i] = next( j[1] for j in bonding_pref if j[0] == count_i )
        else:
            bonding_target[count_i] = N_tot - check_lewis.lone_e[check_lewis.atomic_to_element[int(i.split('[')[1].split(']')[0])]]

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

    # Add/remove electrons depending on the total charge of the molecule
    adjust_ind = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 ]

    # Determine is electrons need to be removed or added
    if q_tot > 0: adjust = -1
    else: adjust = 1

    # Adjust the number of electrons by removing or adding to the available lone pairs
    # The algorithm simply adds/removes from the first N lone pairs that are discovered
    if len(adjust_ind) >= abs(q_tot): 
        for i in range(abs(q_tot)): lone_electrons[adjust_ind[i]] += adjust
    else:
        for i in range(abs(q_tot)): lone_electrons[0] += adjust
        
    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    outer_counter     = 0
    inner_max_cycles  = 5000
    outer_max_cycles  = 5000
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]
    bonds_made = []
    bond_sat = False

    # Check for special chemical groups
    for i in range(len(atomtypes)):

        # Handle nitro groups
        if is_nitro(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            bonds_made += [(i,O_ind[1])]

        # Handle thioketone groups
        if is_thioketone(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the thioketone atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]

    # diagnostic print            
    if verbose is True:
        print( "Starting electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    while bond_sat is False:

        # Initialize necessary objects
        change_list   = range(len(lone_electrons))
        inner_counter = 0
        bond_sat = True                

        # Inner loop forms bonds to remove radicals or underbonded atoms until no further
        # changes in the bonding pattern are observed.
        while len(change_list) > 0:
            change_list = []
            for i in loop_list:

                # List of atoms that already have a satisfactory binding configuration.
                happy = [ j[0] for j in bonding_pref if j[1] == bonding_electrons[j[0]]]            
                
                # If the current atom already has its target configuration then no further action is taken
                if i in happy: continue

                # If there are no lone electrons then skip
                if lone_electrons[i] == 0: continue

                # Take action if this atom has a radical or an unsatifisied bonding condition
                if lone_electrons[i] % 2 != 0 or bonding_electrons[i] != bonding_target[i]:

                    # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                    bonded_radicals = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] % 2 != 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy ]
                    bonded_lonepairs = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] > 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy ]

                    # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                    bonded_radicals = [ j[1] for j in  sorted(bonded_radicals) ]
                    bonded_lonepairs = [ j[1] for j in  sorted(bonded_lonepairs) ]

                    # Correcting radicals is attempted first
                    if len(bonded_radicals) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_radicals[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_radicals[0]] -= 1
                        change_list += [i,bonded_radicals[0]]
                        bonds_made += [(i,bonded_radicals[0])]

                    # Else try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                    elif len(bonded_lonepairs) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_lonepairs[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_lonepairs[0]] -= 1
                        change_list += [i,bonded_lonepairs[0]]
                        bonds_made += [(i,bonded_lonepairs[0])]

            # Increment the counter and break if the maximum number of attempts have been made
            inner_counter += 1
            if inner_counter >= inner_max_cycles:
                print( "WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))

        # Check if the user specified preferred bond order has been achieved.
        if bonding_pref is not None:
            unhappy = [ i[0] for i in bonding_pref if i[1] != bonding_electrons[i[0]]]            
            if len(unhappy) > 0:
                
                # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(adj_mat[unhappy[0]]) if i == 1 ])

                # Check if a rearrangment is possible, break if none are available
                try:
                    break_bond = next( i for i in bonds_made if i[0] in ind or i[1] in ind )
                except:
                    print( "WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                    break

                # Perform bond rearrangment
                bonding_electrons[break_bond[0]] -= 1
                lone_electrons[break_bond[0]] += 1
                bonding_electrons[break_bond[1]] -= 1
                lone_electrons[break_bond[1]] += 1

                # Remove the bond from the list and reorder loop_list so that the indices involved in the bond are put last                
                bonds_made.remove(break_bond)
                loop_list.remove(break_bond[0])
                loop_list.remove(break_bond[1])
                loop_list += [break_bond[0],break_bond[1]]

                # Update the bond_sat flag
                bond_sat = False

            # Increment the counter and break if the maximum number of attempts have been made
            outer_counter += 1

            # Periodically reorder the list to avoid some cyclical walks
            if outer_counter % 100 == 0:
                loop_list = reorder_list(loop_list,atomic_number)

            # Print diagnostic upon failure
            if outer_counter >= outer_max_cycles:
                print( "WARNING: maximum attempts to establish a lewis-structure consistent")
                print( "         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                break

    # diagnostic print            
    if verbose is True:
        print( "\nFinal electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))
        print( "\nbonding_pref: {}\n".format(bonding_pref))

    # Optional bonding pref return to handle cases with special groups
    if return_pref is True:
        return lone_electrons,bonding_electrons,core_electrons,bonding_pref
    else:
        return lone_electrons,bonding_electrons,core_electrons


# Returns a list with the number of electrons on each atom and a list with the number missing/surplus electrons on the atom
# 
# Inputs:  atomtypes: list of atomtypes
#          adj_mat:   np.array of atomic connections
#          q_tot:     total charge on the molecule
#          bonding_pref: optional list of (index, bond_number) tuples that sets the target bond number of the indexed atoms
#          fixed_bonds: optional list of (index_1,index_2,bond_number) tuples that creates fixed bonds between the index_1
#                       and index_2 atoms. No further bonds will be added or subtracted between these atoms.
#
# Returns: lone_electrons:
#          bonding_electrons:
#          core_electrons:
#
def check_lewis(atomtypes,adj_mat,q_tot=0,bonding_pref=[],fixed_bonds=[],return_pref=False,bonds=None,verbose=False):

    # Initialize the preferred lone electron dictionary the first time this function is called
    if not hasattr(check_lewis, "sat_dict"):

        check_lewis.lone_e = {      'h':0, 'he':2,\
                                   'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                                   'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                                    'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                                   'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                                   'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None  }

        # Initialize periodic table
        check_lewis.periodic = { "h": 1,  "he": 2,\
                                 "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                                 "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                                  "k":19, "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                                 "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                                 "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}

        # Initialize periodic table
        check_lewis.atomic_to_element = { check_lewis.periodic[i]:i for i in check_lewis.periodic.keys() }

        # Electronegativity ordering (for determining lewis structure)
    #     check_lews.en_order = [9,8,17,7,36,55,56,16,34,6,81,76,84,80,\
    #                            46,87,79,78,47,45,1,15,33,43,54,53,5,\
    #                            85,31,86,82,51,48,27,77,44,28,14,26,25,\
    #                            30,50,49,23,29,22,83,13,42,4,24,21,93,\
    #                            75,94,95,20,41,12,105,104,103,102,101,\
    #                            100,99,98,97,92,74,96,73,71,70,69,68,\
    #                            40,66,64,62,61,60,91,59,19,3,39,11,90,\
    #                            58,38,19,57,89,2,10,18,63,65,67,72,88]

    # Initalize elementa and atomic_number lists for use by the function
    elements = [ check_lewis.atomic_to_element[int(i.split("[")[1].split("]")[0])] for i in atomtypes ]
    atomic_number = [ int(i.split("[")[1].split("]")[0]) for i in atomtypes ]
    
    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(atomtypes),dtype="int")    
    bonding_electrons = np.zeros(len(atomtypes),dtype="int")    
    core_electrons    = np.zeros(len(atomtypes),dtype="int")
    valence           = np.zeros(len(atomtypes),dtype="int")
    bonding_target    = np.zeros(len(atomtypes),dtype="int")
    for count_i,i in enumerate(atomtypes):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = int(i.split('[')[1].split(']')[0])

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print( "ERROR in check_lewis: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot

        # Assign target number of bonds for this atom
        if count_i in [ j[0] for j in bonding_pref ]:
            bonding_target[count_i] = next( j[1] for j in bonding_pref if j[0] == count_i )
        else:
            bonding_target[count_i] = N_tot - check_lewis.lone_e[check_lewis.atomic_to_element[int(i.split('[')[1].split(']')[0])]]

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    outer_counter     = 0
    inner_max_cycles  = 5000
    outer_max_cycles  = 5000
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]
    bonds_made = []
    bond_sat = False

    # Check for special chemical groups
    for i in range(len(atomtypes)):

        # Handle nitro groups
        if is_nitro(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            bonds_made += [(i,O_ind[1])]

        # Handle sulfoxide groups
        if is_sulfoxide(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the thioketone atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]

        # Handle sulfonyl groups
        if is_sulfonyl(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfoxide atoms from the bonding_pref list
            bonding_pref += [(i,6)]
            bonding_pref += [(O_ind[0],2)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 2
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            bonds_made += [(i,O_ind[0])]
            bonds_made += [(i,O_ind[1])]

        # Handle phosphate groups 
        if is_phosphate(i,adj_mat,elements) is True:
            O_ind      = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] ] # Index of single bonded O-P oxygens
            O_ind_term = [ j for j in O_ind if sum(adj_mat[j]) == 1 ] # Index of double bonded O-P oxygens
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the phosphate atoms from the bonding_pref list
            bonding_pref += [(i,5)]
            bonding_pref += [(O_ind_term[0],2)]  # during testing it ended up being important to only add a bonding_pref tuple for one of the terminal oxygens
            bonding_electrons[O_ind_term[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind_term[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind_term[0])]

        # Handle cyano groups
        if is_cyano(i,adj_mat,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat[count_j]) == 2 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,3)]
            bonding_pref += [(C_ind[0],4)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]

    # Apply fixed_bonds argument
    off_limits=[]
    for i in fixed_bonds:

        # Initalize intermediate variables
        a = i[0]
        b = i[1]
        N = i[2]
        N_current = len([ j for j in bonds_made if (a,b) == j or (b,a) == j ]) + 1

        # Check that a bond exists between these atoms in the adjacency matrix
        if adj_mat[a,b] != 1:
            print( "ERROR in check_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print( "                      but the adjacency matrix doesn't reflect a bond. Exiting...")
            quit()

        # Check that less than or an equal number of bonds exist between these atoms than is requested
        if N_current > N:
            print( "ERROR in check_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print( "                      but {} bonds already exist between these atoms. There may be a conflict".format(N_current))
            print( "                      between the special groups handling and the requested lewis_structure.")
            quit()

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[a] < (N - N_current):
            print( "ERROR in check_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print( "                      but atom {} only has {} lone electrons.".format(a,lone_electrons[a]))

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[b] < (N - N_current):
            print( "ERROR in check_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print( "                      but atom {} only has {} lone electrons.".format(b,lone_electrons[b]))

        # Make the bonds between the atoms
        for j in range(N-N_current):
            bonding_electrons[a] += 1
            bonding_electrons[b] += 1
            lone_electrons[a]    -= 1
            lone_electrons[b]    -= 1
            bonds_made += [ (a,b) ]

        # Append bond to off_limits group so that further bond additions/breaks do not occur.
        off_limits += [(a,b),(b,a)]

    # Turn the off_limits list into a set for rapid lookup
    off_limits = set(off_limits)

    # Add/remove electrons depending on the total charge of the molecule
    happy = [ i[0] for i in bonding_pref if i[1] == bonding_electrons[i[0]]]
    adjust_ind = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy ]

    # Determine is electrons need to be removed or added
    if q_tot > 0: adjust = -1
    else: adjust = 1

    # Adjust the number of electrons by removing or adding to the available lone pairs
    # The algorithm simply adds/removes from the first N lone pairs that are discovered
    if len(adjust_ind) >= abs(q_tot): 
        for i in range(abs(q_tot)): lone_electrons[adjust_ind[i]] += adjust
    else:
        for i in range(abs(q_tot)): lone_electrons[0] += adjust
        


    # diagnostic print            
    if verbose is True:
        print( "Starting electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    while bond_sat is False:

        # Initialize necessary objects
        change_list   = range(len(lone_electrons))
        inner_counter = 0
        bond_sat = True                

        # Inner loop forms bonds to remove radicals or underbonded atoms until no further
        # changes in the bonding pattern are observed.
        while len(change_list) > 0:
            change_list = []
            for i in loop_list:

                # List of atoms that already have a satisfactory binding configuration.
                happy = [ j[0] for j in bonding_pref if j[1] == bonding_electrons[j[0]] ]
                
                # If the current atom already has its target configuration then no further action is taken
                if i in happy: continue

                # If there are no lone electrons then skip
                if lone_electrons[i] == 0: continue

                # Take action if this atom has a radical or an unsatifisied bonding condition
                if lone_electrons[i] % 2 != 0 or bonding_electrons[i] != bonding_target[i]:

                    # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                    bonded_radicals = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] % 2 != 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy and (i,count_j) not in off_limits ]
                    bonded_lonepairs = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] > 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy and (i,count_j) not in off_limits ]

                    # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                    bonded_radicals = [ j[1] for j in  sorted(bonded_radicals) ]
                    bonded_lonepairs = [ j[1] for j in  sorted(bonded_lonepairs) ]

                    # Correcting radicals is attempted first
                    if len(bonded_radicals) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_radicals[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_radicals[0]] -= 1
                        change_list += [i,bonded_radicals[0]]
                        bonds_made += [(i,bonded_radicals[0])]

                    # Else try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                    elif len(bonded_lonepairs) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_lonepairs[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_lonepairs[0]] -= 1
                        change_list += [i,bonded_lonepairs[0]]
                        bonds_made += [(i,bonded_lonepairs[0])]

            # Increment the counter and break if the maximum number of attempts have been made
            inner_counter += 1
            if inner_counter >= inner_max_cycles:
                print( "WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))

        # Check if the user specified preferred bond order has been achieved.
        if bonding_pref is not None:
            unhappy = [ i[0] for i in bonding_pref if i[1] != bonding_electrons[i[0]]]            
            if len(unhappy) > 0:
                
                # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(adj_mat[unhappy[0]]) if i == 1 and (count_i,unhappy[0]) not in off_limits ])

                # Check if a rearrangment is possible, break if none are available
                try:
                    break_bond = next( i for i in bonds_made if i[0] in ind or i[1] in ind )
                except:
                    print( "WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                    break

                # Perform bond rearrangment
                bonding_electrons[break_bond[0]] -= 1
                lone_electrons[break_bond[0]] += 1
                bonding_electrons[break_bond[1]] -= 1
                lone_electrons[break_bond[1]] += 1

                # Remove the bond from the list and reorder loop_list so that the indices involved in the bond are put last                
                bonds_made.remove(break_bond)
                loop_list.remove(break_bond[0])
                loop_list.remove(break_bond[1])
                loop_list += [break_bond[0],break_bond[1]]

                # Update the bond_sat flag
                bond_sat = False

            # Increment the counter and break if the maximum number of attempts have been made
            outer_counter += 1

            # Periodically reorder the list to avoid some cyclical walks
            if outer_counter % 100 == 0:
                loop_list = reorder_list(loop_list,atomic_number)

            # Print diagnostic upon failure
            if outer_counter >= outer_max_cycles:
                print( "WARNING: maximum attempts to establish a lewis-structure consistent")
                print( "         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                break

    # diagnostic print            
    if verbose is True:
        print( "\nFinal electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))
        print( "\nbonding_pref: {}\n".format(bonding_pref))

    # Optional bonding pref return to handle cases with special groups
    if return_pref is True:
        return lone_electrons,bonding_electrons,core_electrons,bonding_pref
    else:
        return lone_electrons,bonding_electrons,core_electrons

# Returns a list with the number of electrons on each atom and a list with the number missing/surplus electrons on the atom
# 
# Inputs:  elements:  a list of element labels indexed to the adj_mat 
#          adj_mat:   np.array of atomic connections
#          bonding_pref: optional list of (index, bond_number) tuples that sets the target bond number of the indexed atoms
#          q_tot:     total charge on the molecule
#          fixed_bonds: optional list of (index_1,index_2,bond_number) tuples that creates fixed bonds between the index_1
#                       and index_2 atoms. No further bonds will be added or subtracted between these atoms.
#
# Optional inputs for ion and radical cases:
#          fc_0:      a list of formal charges on each atom
#          keep_lone: a list of atom index for which contains a radical 
#
# Returns: lone_electrons:
#          bonding_electrons:
#          core_electrons:
#          bond_mat:  an NxN matrix holding the bond orders between all atoms in the adj_mat
#          bonding_pref (optinal): optional list of (index, bond_number) tuples that sets the target bond number of the indexed atoms  
#
def find_lewis(elements,adj_mat_0,bonding_pref=[],q_tot=0,fixed_bonds=[],fc_0=None,keep_lone=[],return_pref=False,verbose=False,b_mat_only=False,return_FC=False,octet_opt=True,check_lewis_flag=False):
    
    # Initialize the preferred lone electron dictionary the first time this function is called
    if not hasattr(find_lewis, "sat_dict"):

        find_lewis.lone_e = {'h':0, 'he':2,\
                             'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                             'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                             'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                             'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                             'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None }

        # Initialize periodic table
        find_lewis.periodic = {  "h": 1,  "he": 2,\
                                 "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                                 "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                                  "k":19, "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                                 "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                                 "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}
        
        # Electronegativity ordering (for determining lewis structure)
        find_lewis.en = { "h" :2.3,  "he":4.16,\
                          "li":0.91, "be":1.58,                                                                                                               "b" :2.05, "c" :2.54, "n" :3.07, "o" :3.61, "f" :4.19, "ne":4.79,\
                          "na":0.87, "mg":1.29,                                                                                                               "al":1.61, "si":1.91, "p" :2.25, "s" :2.59, "cl":2.87, "ar":3.24,\
                          "k" :0.73, "ca":1.03, "sc":1.19, "ti":1.38, "v": 1.53, "cr":1.65, "mn":1.75, "fe":1.80, "co":1.84, "ni":1.88, "cu":1.85, "zn":1.59, "ga":1.76, "ge":1.99, "as":2.21, "se":2.42, "br":2.69, "kr":2.97,\
                          "rb":0.71, "sr":0.96, "y" :1.12, "zr":1.32, "nb":1.41, "mo":1.47, "tc":1.51, "ru":1.54, "rh":1.56, "pd":1.58, "ag":1.87, "cd":1.52, "in":1.66, "sn":1.82, "sb":1.98, "te":2.16, "i" :2.36, "xe":2.58,\
                          "cs":0.66, "ba":0.88, "la":1.09, "hf":1.16, "ta":1.34, "w" :1.47, "re":1.60, "os":1.65, "ir":1.68, "pt":1.72, "au":1.92, "hg":1.76, "tl":1.79, "pb":1.85, "bi":2.01, "po":2.19, "at":2.39, "rn":2.60} 

        # Polarizability ordering (for determining lewis structure)
        find_lewis.pol ={ "h" :4.5,  "he":1.38,\
                          "li":164.0, "be":377,                                                                                                               "b" :20.5, "c" :11.3, "n" :7.4, "o" :5.3,  "f" :3.74, "ne":2.66,\
                          "na":163.0, "mg":71.2,                                                                                                              "al":57.8, "si":37.3, "p" :25.0,"s" :19.4, "cl":14.6, "ar":11.1,\
                          "k" :290.0, "ca":161.0, "sc":97.0, "ti":100.0, "v": 87.0, "cr":83.0, "mn":68.0, "fe":62.0, "co":55, "ni":49, "cu":47.0, "zn":38.7,  "ga":50.0, "ge":40.0, "as":30.0,"se":29.0, "br":21.0, "kr":16.8,\
                          "rb":320.0, "sr":197.0, "y" :162,  "zr":112.0, "nb":98.0, "mo":87.0, "tc":79.0, "ru":72.0, "rh":66, "pd":26.1, "ag":55, "cd":46.0,  "in":65.0, "sn":53.0, "sb":43.0,"te":28.0, "i" :32.9, "xe":27.3,}

        # Bond energy dictionary {}-{}-{} refers to atom1, atom2 additional bonds number (1 refers to double bonds)
        # If energy for multiple bonds is missing, it means it's unusual to form multiple bonds, such value will be -10000.0, if energy for single bonds if missing, directly take multiple bonds energy as the difference 
        # From https://chem.libretexts.org/Bookshelves/Physical_and_Theoretical_Chemistry_Textbook_Maps/Supplemental_Modules_(Physical_and_Theoretical_Chemistry)/Chemical_Bonding/Fundamentals_of_Chemical_Bonding/Bond_Energies
        #find_lewis.be = { "6-6-1": 267, "6-6-2":492, "6-7-1":310, "6-7-2":586, "6-8-1":387, "6-8-2":714, "7-8-1":406, "7-7-1":258, "7-7-2":781, "8-8-1":349, "8-16-1":523, "16-16-1":152}
        # Or from https://www2.chemistry.msu.edu/faculty/reusch/OrgPage/bndenrgy.htm ("6-15-1" is missing)
        # Remove 6-16-1:73
        find_lewis.be = { "6-6-1": 63, "6-6-2":117, "6-7-1":74, "6-7-2":140, "6-8-1":92.5, "6-8-2":172.5, "7-7-1":70.6, "7-7-2":187.6, "7-8-1":88, "8-8-1":84, "8-15-1":20, "8-16-1":6, "15-15-1":84,"15-15-2": 117, "15-16-1":70}
        
        # Initialize periodic table
        find_lewis.atomic_to_element = { find_lewis.periodic[i]:i for i in find_lewis.periodic.keys() }

    # Consistency check on fc_0 argument, if supplied
    if fc_0 is not None:
        if len(fc_0) != len(elements):
            print("ERROR in find_lewis: the fc_0 and elements lists must have the same dimensions.")
            quit()
        if int(sum(fc_0)) != int(q_tot):
            print("ERROR in find_lewis: the sum of formal charges does not equal q_tot.")
            quit()

    # Initalize elementa and atomic_number lists for use by the function
    atomic_number = [ find_lewis.periodic[i.lower()] for i in elements ]
    adj_mat = deepcopy(adj_mat_0)

    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(elements),dtype="int")    
    bonding_electrons = np.zeros(len(elements),dtype="int")    
    core_electrons    = np.zeros(len(elements),dtype="int")
    valence           = np.zeros(len(elements),dtype="int")
    bonding_target    = np.zeros(len(elements),dtype="int")
    valence_list      = np.zeros(len(elements),dtype="int")    
    
    for count_i,i in enumerate(elements):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = atomic_number[count_i]   

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print("ERROR in find_lewis: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot
        valence_list[count_i] = N_tot

        # Assign target number of bonds for this atom
        if count_i in [ j[0] for j in bonding_pref ]:
            bonding_target[count_i] = next( j[1] for j in bonding_pref if j[0] == count_i )
        else:
            bonding_target[count_i] = N_tot - find_lewis.lone_e[elements[count_i].lower()]       

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat_0):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

    # Apply keep_lone: add one electron to such index    
    for count_i in keep_lone:
        lone_electrons[count_i] += 1
        
    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    bonds_made = []    
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]

    # Check for special chemical groups
    for i in range(len(elements)):
        # Handle nitro groups
        if is_nitro(i,adj_mat_0,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            adj_mat[i,O_ind[1]] += 1
            adj_mat[O_ind[1],i] += 1

        # Handle sulfoxide groups
        if is_sulfoxide(i,adj_mat_0,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the thioketone atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[O_ind[0],i] += 1

        # Handle sulfonyl groups
        if is_sulfonyl(i,adj_mat_0,elements) is True:
            
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfoxide atoms from the bonding_pref list
            bonding_pref += [(i,6)]
            bonding_pref += [(O_ind[0],2)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 2
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            bonds_made += [(i,O_ind[0])]
            bonds_made += [(i,O_ind[1])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[i,O_ind[1]] += 1
            adj_mat[O_ind[0],i] += 1
            adj_mat[O_ind[1],i] += 1            
        
        # Handle phosphate groups 
        if is_phosphate(i,adj_mat_0,elements) is True:
            O_ind      = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j] in ["o","O"] ] # Index of single bonded O-P oxygens
            O_ind_term = [ j for j in O_ind if sum(adj_mat_0[j]) == 1 ] # Index of double bonded O-P oxygens
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the phosphate atoms from the bonding_pref list
            bonding_pref += [(i,5)]
            bonding_pref += [(O_ind_term[0],2)]  # during testing it ended up being important to only add a bonding_pref tuple for one of the terminal oxygens
            bonding_electrons[O_ind_term[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind_term[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind_term[0])]
            adj_mat[i,O_ind_term[0]] += 1
            adj_mat[O_ind_term[0],i] += 1

        # Handle cyano groups
        if is_cyano(i,adj_mat_0,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat_0[count_j]) == 2 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,3)]
            bonding_pref += [(C_ind[0],4)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]
            adj_mat[i,C_ind[0]] += 2
            adj_mat[C_ind[0],i] += 2

        # Handle isocyano groups
        if is_isocyano(i,adj_mat,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(C_ind[0],3)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]
            adj_mat[i,C_ind[0]] += 2
            adj_mat[C_ind[0],i] += 2

    # Apply fixed_bonds argument
    off_limits=[]
    for i in fixed_bonds:

        # Initalize intermediate variables
        a = i[0]
        b = i[1]
        N = i[2]
        N_current = len([ j for j in bonds_made if (a,b) == j or (b,a) == j ]) + 1
        # Check that a bond exists between these atoms in the adjacency matrix
        if adj_mat_0[a,b] != 1:
            print("ERROR in find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but the adjacency matrix doesn't reflect a bond. Exiting...")
            quit()

        # Check that less than or an equal number of bonds exist between these atoms than is requested
        if N_current > N:
            print("ERROR in find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but {} bonds already exist between these atoms. There may be a conflict".format(N_current))
            print("                      between the special groups handling and the requested lewis_structure.")
            quit()

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[a] < (N - N_current):
            print("Warning in find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but atom {} only has {} lone electrons.".format(elements[a],lone_electrons[a]))

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[b] < (N - N_current):
            print("Warning in find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but atom {} only has {} lone electrons.".format(elements[b],lone_electrons[b]))
        

        # Make the bonds between the atoms
        for j in range(N-N_current):
            bonding_electrons[a] += 1
            bonding_electrons[b] += 1
            lone_electrons[a]    -= 1
            lone_electrons[b]    -= 1
            bonds_made += [ (a,b) ]

        # Append bond to off_limits group so that further bond additions/breaks do not occur.
        off_limits += [(a,b),(b,a)]

    # Turn the off_limits list into a set for rapid lookup
    off_limits = set(off_limits)
    
    # Adjust formal charges (if supplied)
    if fc_0 is not None:
        for count_i,i in enumerate(fc_0):
            if i > 0:
                #if lone_electrons[count_i] < i:
                    #print "ERROR in find_lewis: atom ({}, index {}) doesn't have enough lone electrons ({}) to be removed to satisfy the specified formal charge ({}).".format(elements[count_i],count_i,lone_electrons[count_i],i)
                    #quit()
                lone_electrons[count_i] = lone_electrons[count_i] - i
            if i < 0:
                lone_electrons[count_i] = lone_electrons[count_i] + int(abs(i))
        q_tot=0
    
    # diagnostic print            
    if verbose is True:
        print("Starting electronic structure:")
        print("\n{:40s} {:20} {:20} {:20} {:20} {}".format("elements","lone_electrons","bonding_electrons","core_electrons","formal_charge","bonded_atoms"))
        for count_i,i in enumerate(elements):
            print("{:40s} {:<20d} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],\
                                                                     valence_list[count_i] - bonding_electrons[count_i] - lone_electrons[count_i],\
                                                                     ",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # Initialize objects for use in the algorithm
    lewis_total = 1000
    lewis_lone_electrons = []
    lewis_bonding_electrons = []
    lewis_core_electrons = []
    lewis_valence = []
    lewis_bonding_target = []
    lewis_bonds_made = []
    lewis_adj_mat = []
    lewis_identical_mat = []
    
    # Determine the atoms with lone pairs that are unsatisfied as candidates for electron removal/addition to satisfy the total charge condition  
    happy = [ i[0] for i in bonding_pref if i[1] <= bonding_electrons[i[0]]]
    bonding_pref_ind = [i[0] for i in bonding_pref]
        
    # Determine is electrons need to be removed or added
    if q_tot > 0:
        adjust = -1
        octet_violate_e = []
        for count_j,j in enumerate(elements):
            if j.lower() in ["c","n","o","f","si","p","s","cl"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] > 8:
                    octet_violate_e += [count_j]
            elif j.lower() in ["br","i"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] > 18:
                    octet_violate_e += [count_j]
        
        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy and count_i not in octet_violate_e]
    
    elif q_tot < 0:
        adjust = 1
        octet_violate_e = []
        for count_j,j in enumerate(elements):
            if j.lower() in ["c","n","o","f","si","p","s","cl"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] < 8:
                    octet_violate_e += [count_j]
                    
            elif j.lower() in ["br","i"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] < 18:
                    octet_violate_e += [count_j]

        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy and count_i not in octet_violate_e]
        
    else:
        adjust = 1
        octet_violate_e = []
        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy ]
    
    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    for dummy_counter in range(lewis_total):
        lewis_loop_list = loop_list
        random.shuffle(lewis_loop_list)
        outer_counter     = 0
        inner_max_cycles  = 1000
        outer_max_cycles  = 1000
        bond_sat = False
        
        lewis_lone_electrons.append(deepcopy(lone_electrons))
        lewis_bonding_electrons.append(deepcopy(bonding_electrons))
        lewis_core_electrons.append(deepcopy(core_electrons))
        lewis_valence.append(deepcopy(valence))
        lewis_bonding_target.append(deepcopy(bonding_target))
        lewis_bonds_made.append(deepcopy(bonds_made))
        lewis_adj_mat.append(deepcopy(adj_mat))
        lewis_counter = len(lewis_lone_electrons) - 1
        
        # Adjust the number of electrons by removing or adding to the available lone pairs
        # The algorithm simply adds/removes from the first N lone pairs that are discovered
        random.shuffle(octet_violate_e)
        random.shuffle(normal_adjust)
        adjust_ind=octet_violate_e+normal_adjust
    
        if len(adjust_ind) >= abs(q_tot): 
            for i in range(abs(q_tot)):
                lewis_lone_electrons[-1][adjust_ind[i]] += adjust
                lewis_bonding_target[-1][adjust_ind[i]] += adjust 
        else:
            for i in range(abs(q_tot)):
                lewis_lone_electrons[-1][0] += adjust
                lewis_bonding_target[-1][0] += adjust

        # Search for an optimal lewis structure
        while bond_sat is False:
        
            # Initialize necessary objects
            change_list   = range(len(lewis_lone_electrons[lewis_counter]))
            inner_counter = 0
            bond_sat = True                
            # Inner loop forms bonds to remove radicals or underbonded atoms until no further
            # changes in the bonding pattern are observed.
            while len(change_list) > 0:
                change_list = []
                for i in lewis_loop_list:

                    # List of atoms that already have a satisfactory binding configuration.
                    happy = [ j[0] for j in bonding_pref if j[1] <= lewis_bonding_electrons[lewis_counter][j[0]]]            
                    
                    # If the current atom already has its target configuration then no further action is taken
                    if i in happy: continue

                    # If there are no lone electrons or too more bond formed then skip
                    if lewis_lone_electrons[lewis_counter][i] == 0: continue
                    
                    # Take action if this atom has a radical or an unsatifisied bonding condition
                    if lewis_lone_electrons[lewis_counter][i] % 2 != 0 or lewis_bonding_electrons[lewis_counter][i] != lewis_bonding_target[lewis_counter][i]:
                        # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                        lewis_bonded_radicals = [ (-find_lewis.en[elements[count_j].lower()],count_j) for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and lewis_lone_electrons[lewis_counter][count_j] % 2 != 0 \
                                                  and 2*(lewis_bonding_electrons[lewis_counter][count_j]+1)+(lewis_lone_electrons[lewis_counter][count_j]-1) <= lewis_valence[lewis_counter][count_j]\
                                                  and lewis_lone_electrons[lewis_counter][count_j]-1 >= 0 and count_j not in happy ]

                        lewis_bonded_lonepairs= [ (-find_lewis.en[elements[count_j].lower()],count_j) for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and lewis_lone_electrons[lewis_counter][count_j] > 0 \
                                                  and 2*(lewis_bonding_electrons[lewis_counter][count_j]+1)+(lewis_lone_electrons[lewis_counter][count_j]-1) <= lewis_valence[lewis_counter][count_j] and lewis_lone_electrons[lewis_counter][count_j]-1 >= 0 \
                                                  and count_j not in happy ]

                        # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                        lewis_bonded_radicals  = [ j[1] for j in sorted(lewis_bonded_radicals) ]
                        lewis_bonded_lonepairs = [ j[1] for j in sorted(lewis_bonded_lonepairs) ]

                        # Correcting radicals is attempted first
                        if len(lewis_bonded_radicals) > 0:
                            lewis_bonding_electrons[lewis_counter][i] += 1
                            lewis_bonding_electrons[lewis_counter][lewis_bonded_radicals[0]] += 1
                            lewis_adj_mat[lewis_counter][i][lewis_bonded_radicals[0]] += 1
                            lewis_adj_mat[lewis_counter][lewis_bonded_radicals[0]][i] += 1 
                            lewis_lone_electrons[lewis_counter][i] -= 1
                            lewis_lone_electrons[lewis_counter][lewis_bonded_radicals[0]] -= 1
                            change_list += [i,lewis_bonded_radicals[0]]
                            lewis_bonds_made[lewis_counter] += [(i,lewis_bonded_radicals[0])]
                                                        
                        # Else try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                        elif len(lewis_bonded_lonepairs) > 0:
                            lewis_bonding_electrons[lewis_counter][i] += 1
                            lewis_bonding_electrons[lewis_counter][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][i][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][lewis_bonded_lonepairs[0]][i] += 1
                            lewis_lone_electrons[lewis_counter][i] -= 1
                            lewis_lone_electrons[lewis_counter][lewis_bonded_lonepairs[0]] -= 1
                            change_list += [i,lewis_bonded_lonepairs[0]]
                            lewis_bonds_made[lewis_counter] += [(i,lewis_bonded_lonepairs[0])]
                            #lewis_bonds_en[lewis_counter] += 1.0/find_lewis.en[elements[i].lower()]/find_lewis.en[elements[lewis_bonded_lonepairs[0]].lower()]
                
                # Increment the counter and break if the maximum number of attempts have been made
                inner_counter += 1
                if inner_counter >= inner_max_cycles:
                    print("WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))
            
            # Check if the user specified preferred bond order has been achieved.
            if bonding_pref is not None:
                unhappy = [ i[0] for i in bonding_pref if i[1] != lewis_bonding_electrons[lewis_counter][i[0]]]            
                if len(unhappy) > 0:

                    # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                    ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(adj_mat_0[unhappy[0]]) if i == 1 and (count_i,unhappy[0]) not in off_limits ])
                    
                    # Check if a rearrangment is possible, break if none are available
                    try:
                        break_bond = next( i for i in lewis_bonds_made[lewis_counter] if i[0] in ind or i[1] in ind )
                    except:
                        print("WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                        break
                    
                    # Perform bond rearrangment
                    lewis_bonding_electrons[lewis_counter][break_bond[0]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[0]] += 1
                    lewis_adj_mat[lewis_counter][break_bond[0]][break_bond[1]] -= 1
                    lewis_adj_mat[lewis_counter][break_bond[1]][break_bond[0]] -= 1
                    lewis_bonding_electrons[lewis_counter][break_bond[1]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[1]] += 1

                    # Remove the bond from the list and reorder lewis_loop_list so that the indices involved in the bond are put last                
                    lewis_bonds_made[lewis_counter].remove(break_bond)
                    lewis_loop_list.remove(break_bond[0])
                    lewis_loop_list.remove(break_bond[1])
                    lewis_loop_list += [break_bond[0],break_bond[1]]
                                        
                    # Update the bond_sat flag
                    bond_sat = False
                    
                # Increment the counter and break if the maximum number of attempts have been made
                outer_counter += 1
                    
                # Periodically reorder the list to avoid some cyclical walks
                if outer_counter % 100 == 0:
                    lewis_loop_list = reorder_list(lewis_loop_list,atomic_number)

                # Print diagnostic upon failure
                if outer_counter >= outer_max_cycles:
                    print("WARNING: maximum attempts to establish a lewis-structure consistent")
                    print("         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                    break
        
        # Re-apply keep_lone: remove one electron from such index    
        for count_i in keep_lone:
            lewis_lone_electrons[lewis_counter][count_i] -= 1

        # Special cases, share pair of electrons
        total_electron=np.array(lewis_lone_electrons[lewis_counter])+np.array(lewis_bonding_electrons[lewis_counter])*2
        
        # count for atom which doesn't satisfy
        # Notice: need systematical check for this part !!!
        unsatisfy = [count_t for count_t,te in enumerate(total_electron) if te > 2 and te < 8 and te % 2 ==0]
        for uns in unsatisfy:
            full_connect=[count_i for count_i,i in enumerate(adj_mat_0[uns]) if i == 1 and total_electron[count_i] == 8 and lewis_lone_electrons[lewis_counter][count_i] >= 2]
            if len(full_connect) > 0:

                lewis_lone_electrons[lewis_counter][full_connect[0]]-=2
                lewis_bonding_electrons[lewis_counter][uns]+=1
                lewis_bonding_electrons[lewis_counter][full_connect[0]]+=1
                lewis_adj_mat[lewis_counter][uns][full_connect[0]]+=1
                lewis_adj_mat[lewis_counter][full_connect[0]][uns]+=1 

        # Delete last entry in the lewis np.arrays if the electronic structure is not unique: introduce identical_mat includes both info of bond_mats and formal_charges
        identical_mat=np.vstack([lewis_adj_mat[-1], np.array([ valence_list[k] - lewis_bonding_electrons[-1][k] - lewis_lone_electrons[-1][k] for k in range(len(elements)) ]) ])
        lewis_identical_mat.append(identical_mat)
        
        if array_unique(lewis_identical_mat[-1],lewis_identical_mat[:-1]) is False :
            lewis_lone_electrons    = lewis_lone_electrons[:-1]
            lewis_bonding_electrons = lewis_bonding_electrons[:-1]
            lewis_core_electrons    = lewis_core_electrons[:-1]
            lewis_valence           = lewis_valence[:-1]
            lewis_bonding_target    = lewis_bonding_target[:-1]
            lewis_bonds_made        = lewis_bonds_made[:-1]
            lewis_adj_mat           = lewis_adj_mat[:-1]
            lewis_identical_mat     = lewis_identical_mat[:-1]
            
    # Find the total number of lone electrons in each structure
    lone_electrons_sums = []
    for i in range(len(lewis_lone_electrons)):
        lone_electrons_sums.append(sum(lewis_lone_electrons[i]))
        
    # Find octet violations in each structure
    octet_violations = []
    for i in range(len(lewis_lone_electrons)):
        ov = 0
        if octet_opt is True:
            for count_j,j in enumerate(elements):
                if j.lower() in ["c","n","o","f","si","p","s","cl","br","i"] and count_j not in bonding_pref_ind:
                    if lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j] != 8 and lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j] != 18:
                        ov += 1
        octet_violations.append(ov)

    ## Calculate bonding energy
    lewis_bonds_energy = []
    for bonds_made in lewis_bonds_made:
        for lb,bond_made in enumerate(bonds_made): bonds_made[lb]=tuple(sorted(bond_made))
        count_bonds_made = ["{}-{}-{}".format(min(atomic_number[bm[0]],atomic_number[bm[1]]),max(atomic_number[bm[0]],atomic_number[bm[1]]),bonds_made.count(bm) ) for bm in set(bonds_made)]
        lewis_bonds_energy += [sum([find_lewis.be[cbm] if cbm in find_lewis.be.keys() else -10000.0 for cbm in count_bonds_made  ]) ]
    # normalize the effect
    lewis_bonds_energy = [-be/max(1,max(lewis_bonds_energy)) for be in lewis_bonds_energy]

    ## Find the total formal charge for each structure
    formal_charges_sums = []
    for i in range(len(lewis_lone_electrons)):
        fc = 0
        for j in range(len(elements)):
            fc += valence_list[j] - lewis_bonding_electrons[i][j] - lewis_lone_electrons[i][j]
        formal_charges_sums.append(fc)
    
    ## Find formal charge eletronegativity contribution
    lewis_formal_charge = [ [ valence_list[i] - lewis_bonding_electrons[_][i] - lewis_lone_electrons[_][i] for i in range(len(elements)) ] for _ in range(len(lewis_lone_electrons)) ]
    lewis_keep_lone     = [ [ count_i for count_i,i in enumerate(lone) if i % 2 != 0] for lone in lewis_lone_electrons]
    lewis_fc_en = []  # Electronegativity for stabling charge/radical
    lewis_fc_pol = [] # Polarizability for stabling charge/radical
    lewis_fc_hc  = [] # Hyper-conjugation contribution
    for i in range(len(lewis_lone_electrons)):
        formal_charge = lewis_formal_charge[i]
        radical_atom = lewis_keep_lone[i]
        fc_ind = [(count_j,j) for count_j,j in enumerate(formal_charge) if j != 0]
        for R_ind in radical_atom:  # assign +0.5 for radical
            fc_ind += [(R_ind,0.5)]
        
        # initialize en,pol and hc
        fc_en,fc_pol,fc_hc = 0,0,0
        
        # Loop over formal charges and radicals
        for count_fc in fc_ind:
            ind = count_fc[0]    
            charge = count_fc[1]
            # Count the self contribution: (-) on the most electronegative atom and (+) on the least electronegative atom
            fc_en += 10 * charge * find_lewis.en[elements[ind].lower()]
             
            # Find the nearest and next-nearest atoms for each formal_charge/radical contained atom
            gs = graph_seps(adj_mat_0)
            nearest_atoms = [count_k for count_k,k in enumerate(lewis_adj_mat[i][ind]) if k >= 1] 
            NN_atoms = list(set([ count_j for count_j,j in enumerate(gs[ind]) if j == 2 ]))
            
            # only count when en > en(C)
            fc_en += charge*(sum([find_lewis.en[elements[count_k].lower()] for count_k in nearest_atoms if find_lewis.en[elements[count_k].lower()] > 2.54] )+\
                             sum([find_lewis.en[elements[count_k].lower()] for count_k in NN_atoms if find_lewis.en[elements[count_k].lower()] > 2.54] ) * 0.1 )

            if charge < 0: # Polarizability only affects negative charge
                fc_pol += charge*sum([find_lewis.pol[elements[count_k].lower()] for count_k in nearest_atoms ])

            # find hyper-conjugation strcuture
            nearby_carbon = [nind for nind in nearest_atoms if elements[nind].lower()=='c']
            for carbon_ind in nearby_carbon:
                carbon_nearby=[nind for nind in NN_atoms if lewis_adj_mat[i][carbon_ind][nind] >= 1 and elements[nind].lower() in ['c','h']]
                if len(carbon_nearby) == 3: fc_hc -= charge*(len([nind for nind in carbon_nearby if elements[nind].lower() == 'c'])*2 + len([nind for nind in carbon_nearby if elements[nind].lower() == 'h']))

        lewis_fc_en.append(fc_en)        
        lewis_fc_pol.append(fc_pol)        
        lewis_fc_hc.append(fc_hc)        

    # normalize the effect
    lewis_fc_en = [lfc/max(1,max(abs(np.array(lewis_fc_en)))) for lfc in lewis_fc_en]
    lewis_fc_pol= [lfp/max(1,max(abs(np.array(lewis_fc_pol)))) for lfp in lewis_fc_pol]
    
    # Add the total number of radicals to the total formal charge to determine the criteria.
    # The radical count is scaled by 0.01 and the lone pair count is scaled by 0.001. This results
    # in the structure with the lowest formal charge always being returned, and the radical count 
    # only being considered if structures with equivalent formal charges are found, and likewise with
    # the lone pair count. The structure(s) with the lowest score will be returned.
    lewis_criteria = []
    for i in range(len(lewis_lone_electrons)):
        #lewis_criteria.append( 10.0*octet_violations[i] + abs(formal_charges_sums[i]) + 0.1*sum([ 1 for j in lewis_lone_electrons[i] if j % 2 != 0 ]) + 0.001*lewis_bonds_energy[i]  + 0.00001*lewis_fc_en[i] + 0.000001*lewis_fc_pol[i] + 0.0000001*lewis_fc_hc[i]) 
        lewis_criteria.append( 10.0*octet_violations[i] + abs(formal_charges_sums[i]) + 0.1*sum([ 1 for j in lewis_lone_electrons[i] if j % 2 != 0 ]) + 0.01*lewis_fc_en[i] + 0.005*lewis_fc_pol[i] +\
                               0.0001*lewis_fc_hc[i] + 0.0001*lewis_bonds_energy[i]) 
    best_lewis = [i[0] for i in sorted(enumerate(lewis_criteria), key=lambda x:x[1])]  # sort from least to most and return a list containing the origial list's indices in the correct order
    best_lewis = [ i for i in best_lewis if lewis_criteria[i] == lewis_criteria[best_lewis[0]] ]    

    # Finally check formal charge to keep those with 
    lewis_re_fc     = [ lewis_formal_charge[_]+lewis_keep_lone[_] for _ in best_lewis]
    appear_times    = [ lewis_re_fc.count(i) for i in lewis_re_fc]
    best_lewis      = [best_lewis[i] for i in range(len(lewis_re_fc)) if appear_times[i] == max(appear_times) ] 
    
    # Apply keep_lone information, remove the electron to form lone electron
    for i in best_lewis:
        for j in keep_lone:
            lewis_lone_electrons[i][j] -= 1

    # Print diagnostics
    if verbose is True:
        for i in best_lewis:
            print("Bonding Matrix  {}".format(i))
            print("Formal_charge:  {}".format(formal_charges_sums[i]))
            print("Lewis_criteria: {}\n".format(lewis_criteria[i]))
            print("{:<40s} {:<40s} {:<15s} {:<15s}".format("Elements","Bond_Mat","Lone_Electrons","FC"))
            for j in range(len(elements)):
                print("{:<40s} {}    {} {}".format(elements[j]," ".join([ str(k) for k in lewis_adj_mat[i][j] ]),lewis_lone_electrons[i][j],valence_list[j] - lewis_bonding_electrons[i][j] - lewis_lone_electrons[i][j]))
            print (" ")

    # If only the bonding matrix is requested, then only that is returned
    if b_mat_only is True:
        if return_FC is False:  
            return [ lewis_adj_mat[_] for _ in best_lewis ]
        else:
            return [ lewis_adj_mat[_] for _ in best_lewis ], [ lewis_formal_charge[_] for _ in best_lewis ]

    # return like check_lewis function
    if check_lewis_flag is True:
        if return_pref is True:
            return lewis_lone_electrons[best_lewis[0]], lewis_bonding_electrons[best_lewis[0]], lewis_core_electrons[best_lewis[0]],bonding_pref
        else:
            return lewis_lone_electrons[best_lewis[0]], lewis_bonding_electrons[best_lewis[0]], lewis_core_electrons[best_lewis[0]]
    
    # Optional bonding pref return to handle cases with special groups
    if return_pref is True:
        if return_FC is False:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],bonding_pref
        else:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],[ lewis_formal_charge[_] for _ in best_lewis ],bonding_pref 

    else:
        if return_FC is False:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ]
        else:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],[ lewis_formal_charge[_] for _ in best_lewis ]

# This function is used to deal with fragments. frag_find_lewis will just form double/triple bonds based on given fc/keep_lone information rather than generate fc/keep_lone.
# 
# Inputs:  elements:  a list of element labels indexed to the adj_mat 
#          adj_mat:   np.array of atomic connections
#          bonding_pref: optional list of (index, bond_number) tuples that sets the target bond number of the indexed atoms
#          q_tot:     total charge on the molecule
#          fixed_bonds: optional list of (index_1,index_2,bond_number) tuples that creates fixed bonds between the index_1
#                       and index_2 atoms. No further bonds will be added or subtracted between these atoms.
#
# Optional inputs for ion and radical cases:
#          fc_0:      a list of formal charges on each atom
#          keep_lone: a list of atom index for which contains a radical 
#
# Returns: lone_electrons:
#          bonding_electrons:
#          core_electrons:
#          bond_mat:  an NxN matrix holding the bond orders between all atoms in the adj_mat
#          bonding_pref (optinal): optional list of (index, bond_number) tuples that sets the target bond number of the indexed atoms  
#
def frag_find_lewis(elements,adj_mat_0,bonding_pref=[],fixed_bonds=[],q_tot=0,fc_0=None,keep_lone=[],return_pref=False,return_FC=False,octet_opt=True,check_lewis_flag=False):

    from itertools import combinations    

    # Initialize the preferred lone electron dictionary the first time this function is called
    if not hasattr(frag_find_lewis, "sat_dict"):

        frag_find_lewis.lone_e = {'h':0, 'he':2,\
                             'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                             'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                             'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                             'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                             'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None }

        # Initialize periodic table
        frag_find_lewis.periodic = { "h": 1,  "he": 2,\
                                 "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                                 "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                                  "k":19, "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                                 "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                                 "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}
        
        # Electronegativity ordering (for determining lewis structure)
        frag_find_lewis.en = { "h" :2.3,  "he":4.16,\
                          "li":0.91, "be":1.58,                                                                                                               "b" :2.05, "c" :2.54, "n" :3.07, "o" :3.61, "f" :4.19, "ne":4.79,\
                          "na":0.87, "mg":1.29,                                                                                                               "al":1.61, "si":1.91, "p" :2.25, "s" :2.59, "cl":2.87, "ar":3.24,\
                          "k" :0.73, "ca":1.03, "sc":1.19, "ti":1.38, "v": 1.53, "cr":1.65, "mn":1.75, "fe":1.80, "co":1.84, "ni":1.88, "cu":1.85, "zn":1.59, "ga":1.76, "ge":1.99, "as":2.21, "se":2.42, "br":2.69, "kr":2.97,\
                          "rb":0.71, "sr":0.96, "y" :1.12, "zr":1.32, "nb":1.41, "mo":1.47, "tc":1.51, "ru":1.54, "rh":1.56, "pd":1.58, "ag":1.87, "cd":1.52, "in":1.66, "sn":1.82, "sb":1.98, "te":2.16, "i" :2.36, "xe":2.58,\
                          "cs":0.66, "ba":0.88, "la":1.09, "hf":1.16, "ta":1.34, "w" :1.47, "re":1.60, "os":1.65, "ir":1.68, "pt":1.72, "au":1.92, "hg":1.76, "tl":1.79, "pb":1.85, "bi":2.01, "po":2.19, "at":2.39, "rn":2.60} 

        # Polarizability ordering (for determining lewis structure)
        frag_find_lewis.pol ={ "h" :4.5,  "he":1.38,\
                          "li":164.0, "be":377,                                                                                                               "b" :20.5, "c" :11.3, "n" :7.4, "o" :5.3,  "f" :3.74, "ne":2.66,\
                          "na":163.0, "mg":71.2,                                                                                                              "al":57.8, "si":37.3, "p" :25.0,"s" :19.4, "cl":14.6, "ar":11.1,\
                          "k" :290.0, "ca":161.0, "sc":97.0, "ti":100.0, "v": 87.0, "cr":83.0, "mn":68.0, "fe":62.0, "co":55, "ni":49, "cu":47.0, "zn":38.7,  "ga":50.0, "ge":40.0, "as":30.0,"se":29.0, "br":21.0, "kr":16.8,\
                          "rb":320.0, "sr":197.0, "y" :162,  "zr":112.0, "nb":98.0, "mo":87.0, "tc":79.0, "ru":72.0, "rh":66, "pd":26.1, "ag":55, "cd":46.0,  "in":65.0, "sn":53.0, "sb":43.0,"te":28.0, "i" :32.9, "xe":27.3,}

        # Bond energy dictionary {}-{}-{} refers to atom1, atom2 additional bonds number (1 refers to double bonds)
        # From https://www2.chemistry.msu.edu/faculty/reusch/OrgPage/bndenrgy.htm 
        # Remove "6-16-1":73
        frag_find_lewis.be = { "6-6-1": 63, "6-6-2":117, "6-7-1":74, "6-7-2":140, "6-8-1":92.5, "6-8-2":172.5, "7-7-1":70.6, "7-7-2":187.6, "7-8-1":88, "8-8-1":84, "8-15-1":20, "8-16-1":6, "15-15-1":84,"15-15-2": 117, "15-16-1":70}

        # Initialize periodic table
        frag_find_lewis.atomic_to_element = { frag_find_lewis.periodic[i]:i for i in frag_find_lewis.periodic.keys() }

    # Consistency check on fc_0 argument, if supplied
    if fc_0 is not None:
        if len(fc_0) != len(elements):
            print("ERROR in frag_find_lewis: the fc_0 and elements lists must have the same dimensions.")
            quit()
        if int(sum(fc_0)) != int(q_tot):
            print("ERROR in frag_find_lewis: the sum of formal charges does not equal q_tot.")
            quit()

    # Initalize elementa and atomic_number lists for use by the function
    atomic_number = [ frag_find_lewis.periodic[i.lower()] for i in elements ]
    adj_mat = deepcopy(adj_mat_0)

    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(elements),dtype="int")    
    bonding_electrons = np.zeros(len(elements),dtype="int")    
    core_electrons    = np.zeros(len(elements),dtype="int")
    valence           = np.zeros(len(elements),dtype="int")
    bonding_target    = np.zeros(len(elements),dtype="int")
    valence_list      = np.zeros(len(elements),dtype="int")    
    
    for count_i,i in enumerate(elements):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = atomic_number[count_i]   

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print("ERROR in frag_find_lewis: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot
        valence_list[count_i] = N_tot

        # Assign target number of bonds for this atom
        if count_i in [ j[0] for j in bonding_pref ]:
            bonding_target[count_i] = next( j[1] for j in bonding_pref if j[0] == count_i )
        else:
            bonding_target[count_i] = N_tot - frag_find_lewis.lone_e[elements[count_i].lower()]       

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat_0):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

    # Apply keep_lone: add one electron to such index    
    for count_i in keep_lone:
        lone_electrons[count_i] += 1
        bonding_target[count_i] -= 1
        
    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    bonds_made = []    
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]

    # Loop over bonding_pref, find whether exist two of them can form bonds
    if len(bonding_pref) > 1:
        bonding_pref_ind = [i[0] for i in bonding_pref]
        comb = combinations(bonding_pref_ind, 2)
        pref_pair = [sorted(pair) for pair in comb if adj_mat_0[pair[0]][pair[1]] == 1]
    else:
        pref_pair = []

    # Check for special chemical groups
    for i in range(len(elements)):

        # Handle nitro groups
        if is_nitro(i,adj_mat_0,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            adj_mat[i,O_ind[1]] += 1
            adj_mat[O_ind[1],i] += 1

        # Handle sulfoxide groups
        if is_frag_sulfoxide(i,adj_mat_0,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the thioketone atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[O_ind[0],i] += 1

        # Handle sulfonyl groups
        if is_frag_sulfonyl(i,adj_mat_0,elements) is True:
            
            O_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j].lower() == "o" and sum(adj_mat_0[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfoxide atoms from the bonding_pref list
            bonding_pref += [(i,6)]
            bonding_pref += [(O_ind[0],2)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 2
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            bonds_made += [(i,O_ind[0])]
            bonds_made += [(i,O_ind[1])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[i,O_ind[1]] += 1
            adj_mat[O_ind[0],i] += 1
            adj_mat[O_ind[1],i] += 1            
        
        # Handle phosphate groups 
        if is_phosphate(i,adj_mat_0,elements) is True:
            O_ind      = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j] in ["o","O"] ] # Index of single bonded O-P oxygens
            O_ind_term = [ j for j in O_ind if sum(adj_mat_0[j]) == 1 ] # Index of double bonded O-P oxygens
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the phosphate atoms from the bonding_pref list
            bonding_pref += [(i,5)]
            bonding_pref += [(O_ind_term[0],2)]  # during testing it ended up being important to only add a bonding_pref tuple for one of the terminal oxygens
            bonding_electrons[O_ind_term[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind_term[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind_term[0])]
            adj_mat[i,O_ind_term[0]] += 1
            adj_mat[O_ind_term[0],i] += 1

        # Handle cyano groups
        if is_cyano(i,adj_mat_0,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat_0[count_j]) == 2 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,3)]
            bonding_pref += [(C_ind[0],4)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]
            adj_mat[i,C_ind[0]] += 2
            adj_mat[C_ind[0],i] += 2

        # Handle isocyano groups
        if is_isocyano(i,adj_mat,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(C_ind[0],3)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]
            adj_mat[i,C_ind[0]] += 2
            adj_mat[C_ind[0],i] += 2
    
    # Apply fixed_bonds argument
    off_limits=[]
    for i in fixed_bonds:

        # Initalize intermediate variables
        a = i[0]
        b = i[1]
        N = i[2]
        N_current = len([ j for j in bonds_made if (a,b) == j or (b,a) == j ]) + 1
        # Check that a bond exists between these atoms in the adjacency matrix
        if adj_mat_0[a,b] != 1:
            print("ERROR in frag_find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but the adjacency matrix doesn't reflect a bond. Exiting...")
            quit()

        # Check that less than or an equal number of bonds exist between these atoms than is requested
        if N_current > N:
            print("ERROR in frag_find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but {} bonds already exist between these atoms. There may be a conflict".format(N_current))
            print("                      between the special groups handling and the requested lewis_structure.")
            quit()

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[a] < (N - N_current):
            print("Warning in frag_find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but atom {} only has {} lone electrons.".format(elements[a],lone_electrons[a]))

        # Check that enough lone electrons exists on each atom to reach the target bond number
        if lone_electrons[b] < (N - N_current):
            print("Warning in frag_find_lewis: fixed_bonds requests bond creation between atoms {} and {} ({} bonds)".format(a,b,N))
            print("                      but atom {} only has {} lone electrons.".format(elements[b],lone_electrons[b]))
        

        # Make the bonds between the atoms
        for j in range(N-N_current):
            bonding_electrons[a] += 1
            bonding_electrons[b] += 1
            lone_electrons[a]    -= 1
            lone_electrons[b]    -= 1
            bonds_made += [ (a,b) ]

        # Append bond to off_limits group so that further bond additions/breaks do not occur.
        off_limits += [(a,b),(b,a)]

    # Turn the off_limits list into a set for rapid lookup
    off_limits = set(off_limits)
            
    # Adjust formal charges (if supplied)
    if fc_0 is not None:
        for count_i,i in enumerate(fc_0):
            if i > 0:
                #if lone_electrons[count_i] < i:
                #    print "ERROR in find_lewis: atom ({}, index {}) doesn't have enough lone electrons ({}) to be removed to satisfy the specified formal charge ({}).".format(elements[count_i],count_i,lone_electrons[count_i],i)
                #    quit()
                lone_electrons[count_i] = lone_electrons[count_i] - i
            if i < 0:
                lone_electrons[count_i] = lone_electrons[count_i] + int(abs(i))
        q_tot=0
        
    # Initialize objects for use in the algorithm
    lewis_total = 1000
    lewis_lone_electrons = []
    lewis_bonding_electrons = []
    lewis_core_electrons = []
    lewis_valence = []
    lewis_bonding_target = []
    lewis_bonds_made = []
    lewis_adj_mat = []
    lewis_identical_mat = []
    
    # Determine the atoms with lone pairs that are unsatisfied as candidates for electron removal/addition to satisfy the total charge condition  
    happy = [ i[0] for i in bonding_pref if i[1] <= bonding_electrons[i[0]]]
    bonding_pref_ind = [i[0] for i in bonding_pref]
    
    # Determine is electrons need to be removed or added
    if q_tot > 0:
        adjust = -1
        octet_violate_e = []
        for count_j,j in enumerate(elements):
            if j.lower() in ["c","n","o","f","si","p","s","cl"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] > 8:
                    octet_violate_e += [count_j]
            elif j.lower() in ["br","i"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] > 18:
                    octet_violate_e += [count_j]
        
        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy and count_i not in octet_violate_e]

    elif q_tot < 0:
        adjust = 1
        octet_violate_e = []
        for count_j,j in enumerate(elements):
            if j.lower() in ["c","n","o","f","si","p","s","cl"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] < 8:
                    octet_violate_e += [count_j]
                    
            elif j.lower() in ["br","i"] and count_j not in bonding_pref_ind:
                if bonding_electrons[count_j]*2 + lone_electrons[count_j] < 18:
                    octet_violate_e += [count_j]

        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy and count_i not in octet_violate_e]
        
    else:
        adjust = 1
        octet_violate_e = []
        normal_adjust = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy ]
    
    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    for dummy_counter in range(lewis_total):
        lewis_loop_list = loop_list
        random.shuffle(lewis_loop_list)
        outer_counter     = 0
        inner_max_cycles  = 1000
        outer_max_cycles  = 1000
        bond_sat = False
        
        lewis_lone_electrons.append(deepcopy(lone_electrons))
        lewis_bonding_electrons.append(deepcopy(bonding_electrons))
        lewis_core_electrons.append(deepcopy(core_electrons))
        lewis_valence.append(deepcopy(valence))
        lewis_bonding_target.append(deepcopy(bonding_target))
        lewis_bonds_made.append(deepcopy(bonds_made))
        lewis_adj_mat.append(deepcopy(adj_mat))
        lewis_counter = len(lewis_lone_electrons) - 1
        
        # Adjust the number of electrons by removing or adding to the available lone pairs
        # The algorithm simply adds/removes from the first N lone pairs that are discovered
        random.shuffle(octet_violate_e)
        random.shuffle(normal_adjust)
        adjust_ind=octet_violate_e+normal_adjust
                
        if len(adjust_ind) >= abs(q_tot): 
            for i in range(abs(q_tot)):
                lewis_lone_electrons[-1][adjust_ind[i]] += adjust
                lewis_bonding_target[-1][adjust_ind[i]] += adjust 
        else:
            for i in range(abs(q_tot)):
                lewis_lone_electrons[-1][0] += adjust
                lewis_bonding_target[-1][0] += adjust
                
        # Search for an optimal lewis structure
        while bond_sat is False:
        
            # Initialize necessary objects
            change_list   = range(len(lewis_lone_electrons[lewis_counter]))
            inner_counter = 0
            bond_sat = True                
            # Inner loop forms bonds to remove radicals or underbonded atoms until no further
            # changes in the bonding pattern are observed.
            while len(change_list) > 0:
                change_list = []
                for i in lewis_loop_list:

                    # List of atoms that already have a satisfactory binding configuration.
                    happy = [ j[0] for j in bonding_pref if j[1] <= lewis_bonding_electrons[lewis_counter][j[0]]]            
                    
                    # If the current atom already has its target configuration then no further action is taken
                    if i in happy: continue

                    # If there are no lone electrons or too more bond formed then skip
                    if lewis_lone_electrons[lewis_counter][i] == 0: continue
                    
                    # Take action if this atom has a radical or an unsatifisied bonding condition
                    if lewis_lone_electrons[lewis_counter][i] % 2 != 0 or lewis_bonding_electrons[lewis_counter][i] != lewis_bonding_target[lewis_counter][i]:
                        # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                        lewis_bonded_lonepairs= [ (-frag_find_lewis.en[elements[count_j].lower()],count_j) for count_j,j in enumerate(adj_mat_0[i]) if j == 1 and lewis_lone_electrons[lewis_counter][count_j] > 0 \
                                                  and 2*(lewis_bonding_electrons[lewis_counter][count_j]+1)+(lewis_lone_electrons[lewis_counter][count_j]-1) <= lewis_valence[lewis_counter][count_j] and\
                                                  lewis_lone_electrons[lewis_counter][count_j]-1 >= 0 and count_j not in happy ]

                        # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                        lewis_bonded_lonepairs = [ j[1] for j in sorted(lewis_bonded_lonepairs) ]
                            
                        # Try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                        if len(lewis_bonded_lonepairs) > 0:
                            lewis_bonding_electrons[lewis_counter][i] += 1
                            lewis_bonding_electrons[lewis_counter][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][i][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][lewis_bonded_lonepairs[0]][i] += 1
                            lewis_lone_electrons[lewis_counter][i] -= 1
                            lewis_lone_electrons[lewis_counter][lewis_bonded_lonepairs[0]] -= 1
                            change_list += [i,lewis_bonded_lonepairs[0]]
                            lewis_bonds_made[lewis_counter] += [(i,lewis_bonded_lonepairs[0])]
                                
                # Increment the counter and break if the maximum number of attempts have been made
                inner_counter += 1
                if inner_counter >= inner_max_cycles:
                    print("WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))
            
            # Check if the user specified preferred bond order has been achieved.
            if bonding_pref is not None:
                unhappy = [ i[0] for i in bonding_pref if i[1] != lewis_bonding_electrons[lewis_counter][i[0]]]            
                if len(unhappy) > 0:

                    # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                    ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(adj_mat_0[unhappy[0]]) if i == 1 and (count_i,unhappy[0]) not in off_limits ])
                    
                    potential_bond = [i for i in lewis_bonds_made[lewis_counter] if ( (i[0] in ind or i[1] in ind ) and (i[0] not in bonding_pref_ind or i[1] not in bonding_pref_ind) ) ]  
                    if len(potential_bond) == 0 :                                                                                                                                                          
                        potential_bond = [i for i in lewis_bonds_made[lewis_counter] if i[0] in ind or i[1] in ind  ]                                                                                          

                    # Check if a rearrangment is possible, break if none are available
                    try:
                        break_bond = next( i for i in potential_bond ) 
                    except:
                        print("WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                        break
                    
                    # Perform bond rearrangment
                    lewis_bonding_electrons[lewis_counter][break_bond[0]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[0]] += 1
                    lewis_adj_mat[lewis_counter][break_bond[0]][break_bond[1]] -= 1
                    lewis_adj_mat[lewis_counter][break_bond[1]][break_bond[0]] -= 1
                    lewis_bonding_electrons[lewis_counter][break_bond[1]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[1]] += 1

                    # Remove the bond from the list and reorder lewis_loop_list so that the indices involved in the bond are put last                
                    lewis_bonds_made[lewis_counter].remove(break_bond)
                    lewis_loop_list.remove(break_bond[0])
                    lewis_loop_list.remove(break_bond[1])
                    lewis_loop_list += [break_bond[0],break_bond[1]]
        
                    # Update the bond_sat flag
                    bond_sat = False
                    
                # Increment the counter and break if the maximum number of attempts have been made
                outer_counter += 1
                    
                # Periodically reorder the list to avoid some cyclical walks
                if outer_counter % 100 == 0:
                    lewis_loop_list = reorder_list(lewis_loop_list,atomic_number)

                # Print diagnostic upon failure
                if outer_counter >= outer_max_cycles:
                    print("WARNING: maximum attempts to establish a lewis-structure consistent")
                    print("         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                    break
                
        # Re-apply keep_lone: remove one electron from such index  
        for count_i in keep_lone:
            lewis_lone_electrons[lewis_counter][count_i] -= 1

        # Delete last entry in the lewis np.arrays if the electronic structure is not unique
        identical_mat=np.vstack([lewis_adj_mat[-1], np.array([ valence_list[k] - lewis_bonding_electrons[-1][k] - lewis_lone_electrons[-1][k] for k in range(len(elements)) ]) ])
        lewis_identical_mat.append(identical_mat)

        if array_unique(lewis_identical_mat[-1],lewis_identical_mat[:-1]) is False :
            lewis_lone_electrons    = lewis_lone_electrons[:-1]
            lewis_bonding_electrons = lewis_bonding_electrons[:-1]
            lewis_core_electrons    = lewis_core_electrons[:-1]
            lewis_valence           = lewis_valence[:-1]
            lewis_bonding_target    = lewis_bonding_target[:-1]
            lewis_bonds_made        = lewis_bonds_made[:-1]
            lewis_adj_mat           = lewis_adj_mat[:-1]
            lewis_identical_mat     = lewis_identical_mat[:-1]
            
    # Find the total number of lone electrons in each structure
    lone_electrons_sums = []
    for i in range(len(lewis_lone_electrons)):
        lone_electrons_sums.append(sum(lewis_lone_electrons[i]))

    # Find octet violations in each structure
    octet_violations = []
    for i in range(len(lewis_lone_electrons)):
        ov = 0
        if octet_opt is True:
            for count_j,j in enumerate(elements):
                if j.lower() in ["c","n","o","f","si","p","s","cl"] and count_j not in bonding_pref_ind:
                    if lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j] < 8:
                        ov += (8 - lewis_bonding_electrons[i][count_j]*2 - lewis_lone_electrons[i][count_j])
                    else:
                        ov += 2 * (lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j]-8)
                if j.lower() in ["br",'i'] and count_j not in bonding_pref_ind:
                    if lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j] < 18:
                        ov += (18 - lewis_bonding_electrons[i][count_j]*2 - lewis_lone_electrons[i][count_j])
                    else:
                        ov += 2 * (lewis_bonding_electrons[i][count_j]*2 + lewis_lone_electrons[i][count_j]-18)
        octet_violations.append(ov)
    
    # Find the total formal charge for each structure
    formal_charges_sums = []
    for i in range(len(lewis_lone_electrons)):
        fc = 0
        for j in range(len(elements)):
            fc += valence_list[j] - lewis_bonding_electrons[i][j] - lewis_lone_electrons[i][j]
        formal_charges_sums.append(fc)
                                   
    # Find formal charge eletronegativity contribution
    lewis_fc_en   = []  # Electronegativity for stabling charge/radical
    lewis_fc_pol  = [] # Polarizability for stabling charge/radical
    lewis_fc_hc   = [] # Hyper-conjugation contribution 
    formal_charge = deepcopy(fc_0)
    radical_atom  = deepcopy(keep_lone)

    # Consider the facts that will stabilize ions/radicals
    for i in range(len(lewis_lone_electrons)):
        fc_ind = [(count_j,j) for count_j,j in enumerate(formal_charge) if j != 0]
        for R_ind in radical_atom:  # assign +0.5 for radical
            fc_ind += [(R_ind,0.5)]
        
        # initialize en,pol and hc
        fc_en,fc_pol,fc_hc = 0,0,0
        
        # Loop over formal charges and radicals
        for count_fc in fc_ind:
            ind = count_fc[0]
            charge = count_fc[1]

            # Count the self contribution: (-) on the most electronegative atom and (+) on the least electronegative atom
            fc_en += 10 * charge * frag_find_lewis.en[elements[ind].lower()]

            # Find the nearest and next-nearest atoms for each formal_charge/radical contained atom
            gs = graph_seps(adj_mat_0)
            nearest_atoms = [count_k for count_k,k in enumerate(lewis_adj_mat[i][ind]) if k >= 1] 
            NN_atoms = list(set([ count_j for count_j,j in enumerate(gs[ind]) if j == 2 ]))
            
            # only count en > en(C)
            fc_en += charge*(sum([frag_find_lewis.en[elements[count_k].lower()] for count_k in nearest_atoms if frag_find_lewis.en[elements[count_k].lower()] > 2.54] )+\
                             sum([frag_find_lewis.en[elements[count_k].lower()] for count_k in NN_atoms if frag_find_lewis.en[elements[count_k].lower()] > 2.54] ) * 0.1 )

            if charge < 0: # Polarizability only affects negative charge ?
                fc_pol += charge*sum([frag_find_lewis.pol[elements[count_k].lower()] for count_k in nearest_atoms ])

            # find hyper-conjugation strcuture
            nearby_carbon = [nind for nind in nearest_atoms if elements[nind].lower()=='c']
            for carbon_ind in nearby_carbon:
                carbon_nearby=[nind for nind in NN_atoms if lewis_adj_mat[i][carbon_ind][nind] >= 1 and elements[nind].lower() in ['c','h']]
                radical_on_carbon = lewis_lone_electrons[i][carbon_ind]
                if (len(carbon_nearby)+radical_on_carbon) == 3: fc_hc -= charge*(len([nind for nind in carbon_nearby if elements[nind].lower() == 'c']) * 2 +\
                                                                                 len([nind for nind in carbon_nearby if elements[nind].lower() == 'h']) + radical_on_carbon )
            
        lewis_fc_en.append(fc_en)        
        lewis_fc_pol.append(fc_pol)        
        lewis_fc_hc.append(fc_hc)        
    # normalize the effect
    lewis_fc_en = [lfc/max(1,max(abs(np.array(lewis_fc_en)))) for lfc in lewis_fc_en]
    lewis_fc_pol= [lfp/max(1,max(abs(np.array(lewis_fc_pol)))) for lfp in lewis_fc_pol]

    # The bond formation will try to keep resonance structures
    # First find identical atoms; then determine whether the distance between them is 2, if so, find the connecting atom to this pair to form two "resonance preferance pairs". After
    # finding all such pairs, count it in lewis critria.
    mass_dict = {'H':1.00794,'He':4.002602,'Li':6.941,'Be':9.012182,'B':10.811,'C':12.011,'N':14.00674,'O':15.9994,'F':18.9984032,'Ne':20.1797,\
                 'Na':22.989768,'Mg':24.3050,'Al':26.981539,'Si':28.0855,'P':30.973762,'S':32.066,'Cl':35.4527,'Ar':39.948,\
                 'K':39.0983,'Ca':40.078,'Sc':44.955910,'Ti':47.867,'V':50.9415,'Cr':51.9961,'Mn':54.938049,'Fe':55.845,'Co':58.933200,'Ni':58.6934,'Cu':63.546,'Zn':65.39,\
                 'Ga':69.723,'Ge':72.61,'As':74.92159,'Se':78.96,'Br':79.904,'Kr':83.80,\
                 'Rb':85.4678,'Sr':87.62,'Y':88.90585,'Zr':91.224,'Nb':92.90638,'Mo':95.94,'Tc':98.0,'Ru':101.07,'Rh':102.90550,'Pd':106.42,'Ag':107.8682,'Cd':112.411,\
                 'In':114.818,'Sn':118.710,'Sb':121.760,'Te':127.60,'I':126.90447,'Xe':131.29,\
                 'Cs':132.90545,'Ba':137.327,'La':138.9055,'Hf':178.49,'Ta':180.9479,'W':183.84,'Re':186.207,'Os':190.23,'Ir':192.217,'Pt':195.078,'Au':196.96655,'Hg':200.59,\
                 'Tl':204.3833,'Pb':207.2,'Bi':208.98038,'Po':209.0,'At':210.0,'Rn':222.0}
    masses    = [ mass_dict[i] for i in elements ]
    hash_list = [  atom_hash(ind,adj_mat_0,masses) for ind in range(len(elements)) ]

    # Find identical atoms
    same_atoms= [(i,[ count_j for count_j,j in enumerate(hash_list) if j == i ]  ) for i in set(hash_list) if hash_list.count(i) > 1]
    gs = graph_seps(adj_mat_0) 
    res_atoms = []
    
    # Keep identical atoms whose distance = 2
    for i in same_atoms:
        if len(i[1]) == 2 and gs[i[1][0]][i[1][1]] == 2: res_atoms += [ [tuple(i[1]),2]]
        if len(i[1]) > 2:
            comb = combinations(i[1], 2)
            res_atoms += [ [j,len(i[1])] for j in comb if gs[j[0]][j[1]] == 2 ]
    
    # Find connecting atom to form resonance pairs
    res_pair = []
    res_pair_score = []
    for pair_list in res_atoms:
        pair = pair_list[0]
        center_atom = [ ind for ind,i in enumerate(adj_mat_0[pair[0]]) if i==1 and adj_mat_0[pair[1]][ind] ==1 ][0]
        res_pair += [ tuple(sorted((pair[0],center_atom))),tuple(sorted((pair[1],center_atom)))]
        res_pair_score += [pair_list[1],pair_list[1]]
    
    # loop over lewis_bonds_made to determine the lewis criteria
    lewis_res_bonds = []    
    lewis_bonds_energy = []
    for bonds_made in lewis_bonds_made:
        res_bonds = 0
        bonds_energy = 0
        for lb,bond_made in enumerate(bonds_made): bonds_made[lb]=tuple(sorted(bond_made))
        for bond_made in bonds_made:
            # in the bonds in res_pair, enlarge by the number of symmetry atoms
            if bond_made in res_pair:
                res_bonds += res_pair_score[res_pair.index(bond_made)]
            # if the bonds in pref_bonds, enlarge the effect by 2; for cation, prefer to form bonds while for anion/radical prefer to keep single bond
            factor = 0.1 # make bonds_energy comparable with originally used bonds_en
            if sorted([bond_made[0],bond_made[1]]) in pref_pair : factor *= 2 
            if fc_0[bond_made[0]] > 0 or fc_0[bond_made[1]] > 0 : factor *= 2 
            if fc_0[bond_made[0]] < 0 or fc_0[bond_made[1]] < 0 : factor *= 0.5
            if bond_made[0] in keep_lone or bond_made[1] in keep_lone : factor *= 0.5
            bond_type = "{}-{}-{}".format(min(atomic_number[bond_made[0]],atomic_number[bond_made[1]]),max(atomic_number[bond_made[0]],atomic_number[bond_made[1]]),bonds_made.count(bond_made))
            if bond_type in frag_find_lewis.be.keys(): bonds_energy += factor * frag_find_lewis.be[bond_type]
            else: bonds_energy -= factor * (-10000.0)
        lewis_bonds_energy += [bonds_energy]
        lewis_res_bonds += [res_bonds]
    # normalize the effect
    lewis_bonds_energy = [-be/max(1,max(lewis_bonds_energy)) for be in lewis_bonds_energy]
    lewis_res_bonds    = [-re/max(1,max(lewis_res_bonds)) for re in lewis_res_bonds]
    
    # Add the total number of radicals to the total formal charge to determine the criteria.
    # The radical count is scaled by 0.01 and the lone pair count is scaled by 0.001. This results
    # in the structure with the lowest formal charge always being returned, and the radical count 
    # only being considered if structures with equivalent formal charges are found, and likewise with
    # the lone pair count. The structure(s) with the lowest score will be returned.
    lewis_criteria = []
    for i in range(len(lewis_lone_electrons)):
        lewis_criteria.append( 10.0*octet_violations[i] + lewis_fc_en[i] + lewis_fc_pol[i] + 0.1 * lewis_fc_hc[i] + 0.01 * lewis_bonds_energy[i] + 0.0001 * lewis_res_bonds[i] )

    best_lewis = [i[0] for i in sorted(enumerate(lewis_criteria), key=lambda x:x[1])]  # sort from least to most and return a list containing the origial list's indices in the correct order
    best_lewis = [ i for i in best_lewis if lewis_criteria[i] == lewis_criteria[best_lewis[0]] ]

    # Apply keep_lone information, remove the electron to form lone electron
    for i in best_lewis:
        for j in keep_lone:
            lewis_lone_electrons[i][j] -= 1

    # return check_lewis function
    if check_lewis_flag is True:
        if return_pref is True:
            return lewis_lone_electrons[best_lewis[0]], lewis_bonding_electrons[best_lewis[0]], lewis_core_electrons[best_lewis[0]],bonding_pref
        else:
            return lewis_lone_electrons[best_lewis[0]], lewis_bonding_electrons[best_lewis[0]], lewis_core_electrons[best_lewis[0]]
    
    # Optional bonding pref return to handle cases with special groups
    if return_pref is True:
        if return_FC is False:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],bonding_pref
        else:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],\
                   [ [ valence_list[i] - lewis_bonding_electrons[_][i] - lewis_lone_electrons[_][i] for i in range(len(elements)) ] for _ in best_lewis ],bonding_pref

    else:
        if return_FC is False:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ]
        else:
            return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
                   [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],\
                   [ [ valence_list[i] - lewis_bonding_electrons[_][i] - lewis_lone_electrons[_][i] for i in range(len(elements)) ] for _ in best_lewis ]
    


# Returns an NxN matrix holding the bond orders between all atoms in the molecular structure.
# 
# Inputs:  elements:  a list of element labels indexed to the adj_mat
#          adj_mat:   a list of bonds indexed to the elements list
#
# Returns: 
#          bond_mat:  an NxN matrix holding the bond orders between all atoms in the adj_mat
#
'''
def find_lewis(atomtypes,adj_mat_0,bonding_pref=[],q_tot=0,return_pref=False,verbose=False,b_mat_only=False):

    # Initialize the preferred lone electron dictionary the first time this function is called
    if not hasattr(find_lewis, "sat_dict"):

        find_lewis.lone_e = {      'h':0, 'he':2,\
                                   'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                                   'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                                    'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                                   'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                                   'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None  }

        # Initialize periodic table
        find_lewis.periodic = { "h": 1,  "he": 2,\
                                 "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                                 "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                                  "k":19, "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                                 "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                                 "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}
        
        # Initialize periodic table
        find_lewis.atomic_to_element = { find_lewis.periodic[i]:i for i in find_lewis.periodic.keys() }

        # Electronegativity ordering (for determining lewis structure)
    #     check_lews.en_order = [9,8,17,7,36,55,56,16,34,6,81,76,84,80,\
    #                            46,87,79,78,47,45,1,15,33,43,54,53,5,\
    #                            85,31,86,82,51,48,27,77,44,28,14,26,25,\
    #                            30,50,49,23,29,22,83,13,42,4,24,21,93,\
    #                            75,94,95,20,41,12,105,104,103,102,101,\
    #                            100,99,98,97,92,74,96,73,71,70,69,68,\
    #                            40,66,64,62,61,60,91,59,19,3,39,11,90,\
    #                            58,38,19,57,89,2,10,18,63,65,67,72,88]

    # Initalize elementa and atomic_number lists for use by the function
    elements = [ find_lewis.atomic_to_element[int(i.split("[")[1].split("]")[0])] for i in atomtypes ]
    atomic_number = [ int(i.split("[")[1].split("]")[0]) for i in atomtypes ]
    adj_mat = deepcopy(adj_mat_0)
    
    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(atomtypes),dtype="int")    
    bonding_electrons = np.zeros(len(atomtypes),dtype="int")    
    core_electrons    = np.zeros(len(atomtypes),dtype="int")
    valence           = np.zeros(len(atomtypes),dtype="int")
    bonding_target    = np.zeros(len(atomtypes),dtype="int")
    valence_list      = np.zeros(len(atomtypes),dtype="int")    
    
    for count_i,i in enumerate(atomtypes):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = int(i.split('[')[1].split(']')[0])

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print( "ERROR in find_lewis: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot
        valence_list[count_i] = N_tot

        # Assign target number of bonds for this atom
        if count_i in [ j[0] for j in bonding_pref ]:
            bonding_target[count_i] = next( j[1] for j in bonding_pref if j[0] == count_i )
        else:
            bonding_target[count_i] = N_tot - find_lewis.lone_e[find_lewis.atomic_to_element[int(i.split('[')[1].split(']')[0])]]

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

#     # Add/remove electrons depending on the total charge of the molecule
#     adjust_ind = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 ]

#     # Determine is electrons need to be removed or added
#     if q_tot > 0: adjust = -1
#     else: adjust = 1

#     # Adjust the number of electrons by removing or adding to the available lone pairs
#     # The algorithm simply adds/removes from the first N lone pairs that are discovered
#     if len(adjust_ind) >= abs(q_tot): 
#         for i in range(abs(q_tot)): lone_electrons[adjust_ind[i]] += adjust
#     else:
#         for i in range(abs(q_tot)): lone_electrons[0] += adjust

    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    bonds_made = []    
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]

    # Check for special chemical groups
    for i in range(len(atomtypes)):

        # Handle nitro groups
        if is_nitro(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            adj_mat[i,O_ind[0]] += 1
            adj_mat[O_ind[0],i] += 1

        # Handle sulfoxide groups
        if is_sulfoxide(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the thioketone atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[O_ind[0],i] += 1

        # Handle sulfonyl groups
        if is_sulfonyl(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] == "o" and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfoxide atoms from the bonding_pref list
            bonding_pref += [(i,6)]
            bonding_pref += [(O_ind[0],2)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 2
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            bonds_made += [(i,O_ind[0])]
            bonds_made += [(i,O_ind[1])]
            adj_mat[i,O_ind[0]] += 1
            adj_mat[i,O_ind[1]] += 1
            adj_mat[O_ind[0],i] += 1
            adj_mat[O_ind[1],i] += 1            

        # Handle phosphate groups 
        if is_phosphate(i,adj_mat,elements) is True:
            O_ind      = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] ] # Index of single bonded O-P oxygens
            O_ind_term = [ j for j in O_ind if sum(adj_mat[j]) == 1 ] # Index of double bonded O-P oxygens
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the phosphate atoms from the bonding_pref list
            bonding_pref += [(i,5)]
            bonding_pref += [(O_ind_term[0],2)]  # during testing it ended up being important to only add a bonding_pref tuple for one of the terminal oxygens
            bonding_electrons[O_ind_term[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind_term[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind_term[0])]
            adj_mat[i,O_ind_term[0]] += 1
            adj_mat[O_ind_term[0],i] += 1

        # Handle cyano groups
        if is_cyano(i,adj_mat,elements) is True:
            C_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in  ["c","C"] and sum(adj_mat[count_j]) == 2 ]
            bonding_pref  = [ j for j in bonding_pref if j[0] != i and j[0] not in C_ind ] # remove bonds involving the cyano atoms from the bonding_pref list
            bonding_pref += [(i,3)]
            bonding_pref += [(C_ind[0],4)]
            bonding_electrons[C_ind[0]] += 2
            bonding_electrons[i] += 2
            lone_electrons[C_ind[0]] -= 2
            lone_electrons[i] -= 2
            bonds_made += [(i,C_ind[0])]
            bonds_made += [(i,C_ind[0])]
            adj_mat[i,C_ind[0]] += 2
            adj_mat[C_ind[0],i] += 2

    # diagnostic print            
    if verbose is True:
        print( "Starting electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # Initialize objects for use in the algorithm
    lewis_total = 1000
    lewis_lone_electrons = []
    lewis_bonding_electrons = []
    lewis_core_electrons = []
    lewis_valence = []
    lewis_bonding_target = []
    lewis_bonds_made = []
    lewis_adj_mat = []

    # Determine the atoms with lone pairs that are unsatisfied as candidates for electron removal/addition to satisfy the total charge condition
    happy = [ i[0] for i in bonding_pref if i[1] == bonding_electrons[i[0]]]
    adjust_ind = [ count_i for count_i,i in enumerate(lone_electrons) if i > 0 and count_i not in happy ]

    # Determine if electrons need to be removed or added
    if q_tot > 0: adjust = -1
    else: adjust = 1
    
    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    for dummy_counter in range(lewis_total):
        lewis_loop_list = loop_list
        random.shuffle(lewis_loop_list)
        outer_counter     = 0
        inner_max_cycles  = 5000
        outer_max_cycles  = 5000
        bond_sat = False
        
        lewis_lone_electrons.append(deepcopy(lone_electrons))
        lewis_bonding_electrons.append(deepcopy(bonding_electrons))
        lewis_core_electrons.append(deepcopy(core_electrons))
        lewis_valence.append(deepcopy(valence))
        lewis_bonding_target.append(deepcopy(bonding_target))
        lewis_bonds_made.append(deepcopy(bonds_made))
        lewis_adj_mat.append(deepcopy(adj_mat))
        lewis_counter = len(lewis_lone_electrons) - 1

        # Adjust the number of electrons by removing or adding to the available lone pairs
        # The algorithm simply adds/removes from the first N lone pairs that are discovered
        random.shuffle(adjust_ind)
        if len(adjust_ind) >= abs(q_tot): 
            for i in range(abs(q_tot)): lewis_lone_electrons[-1][adjust_ind[i]] += adjust
        else:
            for i in range(abs(q_tot)): lewis_lone_electrons[-1][0] += adjust

        # Search for an optimal lewis structure
        while bond_sat is False:
        
            # Initialize necessary objects
            change_list   = range(len(lewis_lone_electrons[lewis_counter]))
            inner_counter = 0
            bond_sat = True                

            # Inner loop forms bonds to remove radicals or underbonded atoms until no further
            # changes in the bonding pattern are observed.
            while len(change_list) > 0:
                change_list = []
                for i in lewis_loop_list:

                    # List of atoms that already have a satisfactory binding configuration.
                    happy = [ j[0] for j in bonding_pref if j[1] == bonding_electrons[j[0]]]            

                    # If the current atom already has its target configuration then no further action is taken
                    if i in happy: continue

                    # If there are no lone electrons then skip
                    if lewis_lone_electrons[lewis_counter][i] == 0: continue

                    # Take action if this atom has a radical or an unsatifisied bonding condition
                    if lewis_lone_electrons[lewis_counter][i] % 2 != 0 or lewis_bonding_electrons[lewis_counter][i] != lewis_bonding_target[lewis_counter][i]:

                        # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                        lewis_bonded_radicals = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(lewis_adj_mat[lewis_counter][i]) if j == 1 and lewis_lone_electrons[lewis_counter][count_j] % 2 != 0 \
                                           and 2*(lewis_bonding_electrons[lewis_counter][count_j]+1)+(lewis_lone_electrons[lewis_counter][count_j]-1) <= lewis_valence[lewis_counter][count_j] and lewis_lone_electrons[lewis_counter][count_j]-1 >= 0 and count_j not in happy ]
                        lewis_bonded_lonepairs = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(lewis_adj_mat[lewis_counter][i]) if j == 1 and lewis_lone_electrons[lewis_counter][count_j] > 0 \
                                           and 2*(lewis_bonding_electrons[lewis_counter][count_j]+1)+(lewis_lone_electrons[lewis_counter][count_j]-1) <= lewis_valence[lewis_counter][count_j] and lewis_lone_electrons[lewis_counter][count_j]-1 >= 0 and count_j not in happy ]

                        # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                        lewis_bonded_radicals = [ j[1] for j in  sorted(lewis_bonded_radicals) ]
                        lewis_bonded_lonepairs = [ j[1] for j in  sorted(lewis_bonded_lonepairs) ]

                        # Correcting radicals is attempted first
                        if len(lewis_bonded_radicals) > 0:
                            lewis_bonding_electrons[lewis_counter][i] += 1
                            lewis_bonding_electrons[lewis_counter][lewis_bonded_radicals[0]] += 1
                            lewis_adj_mat[lewis_counter][i][lewis_bonded_radicals[0]] += 1
                            lewis_adj_mat[lewis_counter][lewis_bonded_radicals[0]][i] += 1  #here
                            lewis_lone_electrons[lewis_counter][i] -= 1
                            lewis_lone_electrons[lewis_counter][lewis_bonded_radicals[0]] -= 1
                            change_list += [i,lewis_bonded_radicals[0]]
                            lewis_bonds_made[lewis_counter] += [(i,lewis_bonded_radicals[0])]

                        # Else try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                        elif len(lewis_bonded_lonepairs) > 0:
                            lewis_bonding_electrons[lewis_counter][i] += 1
                            lewis_bonding_electrons[lewis_counter][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][i][lewis_bonded_lonepairs[0]] += 1
                            lewis_adj_mat[lewis_counter][lewis_bonded_lonepairs[0]][i] += 1
                            lewis_lone_electrons[lewis_counter][i] -= 1
                            lewis_lone_electrons[lewis_counter][lewis_bonded_lonepairs[0]] -= 1
                            change_list += [i,lewis_bonded_lonepairs[0]]
                            lewis_bonds_made[lewis_counter] += [(i,lewis_bonded_lonepairs[0])]

                # Increment the counter and break if the maximum number of attempts have been made
                inner_counter += 1
                if inner_counter >= inner_max_cycles:
                    print( "WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))

            # Check if the user specified preferred bond order has been achieved.
            if bonding_pref is not None:
                unhappy = [ i[0] for i in bonding_pref if i[1] != lewis_bonding_electrons[lewis_counter][i[0]]]            
                if len(unhappy) > 0:
                
                    # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                    ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(lewis_adj_mat[lewis_counter][unhappy[0]]) if i == 1 ])

                    # Check if a rearrangment is possible, break if none are available
                    try:
                        break_bond = next( i for i in bonds_made if i[0] in ind or i[1] in ind )
                    except:
                        print( "WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                        break

                    # Perform bond rearrangment
                    lewis_bonding_electrons[lewis_counter][break_bond[0]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[0]] += 1
                    lewis_adj_mat[lewis_counter][unhappy[0]][break_bond[0]] -= 1
                    lewis_adj_mat[lewis_counter][break_bond[0]][unhappy[0]] -= 1
                    lewis_bonding_electrons[lewis_counter][break_bond[1]] -= 1
                    lewis_lone_electrons[lewis_counter][break_bond[1]] += 1

                    # Remove the bond from the list and reorder lewis_loop_list so that the indices involved in the bond are put last                
                    lewis_bonds_made[lewis_counter].remove(break_bond)
                    lewis_loop_list.remove(break_bond[0])
                    lewis_loop_list.remove(break_bond[1])
                    lewis_loop_list += [break_bond[0],break_bond[1]]

                    # Update the bond_sat flag
                    bond_sat = False

                # Increment the counter and break if the maximum number of attempts have been made
                outer_counter += 1

                # Periodically reorder the list to avoid some cyclical walks
                if outer_counter % 100 == 0:
                    lewis_loop_list = reorder_list(lewis_loop_list,atomic_number)

                # Print diagnostic upon failure
                if outer_counter >= outer_max_cycles:
                    print( "WARNING: maximum attempts to establish a lewis-structure consistent")
                    print( "         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                    break
            
        # Delete last entry in the lewis np.arrays if the electronic structure is not unique
        if array_unique(lewis_adj_mat[-1],lewis_adj_mat[:-1]) is False:
            lewis_lone_electrons    = lewis_lone_electrons[:-1]
            lewis_bonding_electrons = lewis_bonding_electrons[:-1]
            lewis_core_electrons    = lewis_core_electrons[:-1]
            lewis_valence           = lewis_valence[:-1]
            lewis_bonding_target    = lewis_bonding_target[:-1]
            lewis_bonds_made        = lewis_bonds_made[:-1]
            lewis_adj_mat           = lewis_adj_mat[:-1]

    # Find the total number of lone electrons in each structure
    lone_electrons_sums = []
    for i in range(len(lewis_lone_electrons)):
        lone_electrons_sums.append(sum(lewis_lone_electrons[i]))
    
    # Find the total formal charge for each structure
    formal_charges_sums = []
    for i in range(len(lewis_lone_electrons)):
        fc = 0
        for j in range(len(atomtypes)):
            fc += valence_list[j] - lewis_bonding_electrons[i][j] - lewis_lone_electrons[i][j]
        formal_charges_sums.append(fc)

    # Add the total number of radicals to the total formal charge to determine the criteria.
    # The radical count is scaled by 0.01 and the lone pair count is scaled by 0.001. This results
    # in the structure with the lowest formal charge always being returned, and the radical count 
    # only being considered if structures with equivalent formal charges are found, and likewise with
    # the lone pair count. The structure(s) with the lowest score will be returned.
    lewis_criteria = []
    for i in range(len(lewis_lone_electrons)):
        lewis_criteria.append( abs(formal_charges_sums[i]) + 0.01*sum([ j for j in lewis_lone_electrons[i] if j % 2 != 0 ]) + 0.0001*sum([ j for j in lewis_lone_electrons[i] if j % 2 == 0 ]) )

    best_lewis = [i[0] for i in sorted(enumerate(lewis_criteria), key=lambda x:x[1])]  # sort from least to most and return a list containing the origial list's indices in the correct order
    best_lewis = [ i for i in best_lewis if lewis_criteria[i] == lewis_criteria[best_lewis[0]] ]

    # Print diagnostics
    if verbose is True:
        for i in best_lewis:
            print( "Bonding Matrix  {}".format(i))
            print( "Formal_charge:  {}".format(formal_charges_sums[i]))
            print( "Lewis_criteria: {}\n".format(lewis_criteria[i]))
            for j in range(len(atomtypes)):
                print( "{:<40s} {}    {} {}".format(atomtypes[j]," ".join([ str(k) for k in lewis_adj_mat[i][j] ]),lewis_lone_electrons[i][j],valence_list[j] - lewis_bonding_electrons[i][j] - lewis_lone_electrons[i][j]))
            print( " ")

    # If only the bonding matrix is requested, then only that is returned
    if b_mat_only is True:
        return [ lewis_adj_mat[_] for _ in best_lewis ]

    # Optional bonding pref return to handle cases with special groups
    if return_pref is True:
        return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
               [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],[ formal_charges_sums[_] for _ in best_lewis ],bonding_pref
    else:
        return [ lewis_lone_electrons[_] for _ in best_lewis ],[ lewis_bonding_electrons[_] for _ in best_lewis ],\
               [ lewis_core_electrons[_] for _ in best_lewis ],[ lewis_adj_mat[_] for _ in best_lewis ],[ formal_charges_sums[_] for _ in best_lewis ]
'''
# Description: Checks if an np.array "a" is unique compared with a list of np.arrays "a_list"
#              at the first match False is returned.
def array_unique(a,a_list):
    for i in a_list:
        if np.array_equal(a,i):
            return False
    return True

# Returns an NxN matrix holding the bond orders between all atoms in the molecular structure.
# 
# Inputs:  elements:  a list of element labels indexed to the adj_mat
#          adj_mat:   a list of bonds indexed to the elements list
#
# Returns: 
#          bond_mat:  an NxN matrix holding the bond orders between all atoms in the adj_mat
#
def get_bonds(elements,adj_mat,verbose=False):

    # Initialize the saturation dictionary the first time this function is called
    if not hasattr(get_bonds, "sat_dict"):
        get_bonds.sat_dict = {  'H':1, 'He':1,\
                               'Li':1, 'Be':2,                                                                                                                'B':3,     'C':4,     'N':3,     'O':2,     'F':1,    'Ne':1,\
                               'Na':1, 'Mg':2,                                                                                                               'Al':3,    'Si':4,     'P':3,     'S':2,    'Cl':1,    'Ar':1,\
                                'K':1, 'Ca':2, 'Sc':None, 'Ti':None,  'V':None, 'Cr':None, 'Mn':None, 'Fe':None, 'Co':None, 'Ni':None, 'Cu':None, 'Zn':None, 'Ga':None, 'Ge':None, 'As':None, 'Se':None, 'Br':1,    'Kr':None,\
                               'Rb':1, 'Sr':2,  'Y':None, 'Zr':None, 'Nb':None, 'Mo':None, 'Tc':None, 'Ru':None, 'Rh':None, 'Pd':None, 'Ag':None, 'Cd':None, 'In':None, 'Sn':None, 'Sb':None, 'Te':None,  'I':1,    'Xe':None,\
                               'Cs':1, 'Ba':2, 'La':None, 'Hf':None, 'Ta':None,  'W':None, 'Re':None, 'Os':None, 'Ir':None, 'Pt':None, 'Au':None, 'Hg':None, 'Tl':None, 'Pb':None, 'Bi':None, 'Po':None, 'At':None, 'Rn':None  }


        # Initialize periodic table
        get_bonds.periodic = { "h": 1,  "he": 2,\
                              "li":3,  "be":4,                                                                                                      "b":5,    "c":6,    "n":7,    "o":8,    "f":9,    "ne":10,\
                              "na":11, "mg":12,                                                                                                     "al":13,  "si":14,  "p":15,   "s":16,   "cl":17,  "ar":18,\
                               "k":19,  "ca":20,  "sc":21,  "ti":22,  "v":23,  "cr":24,  "mn":25,  "fe":26,  "co":27,  "ni":28,  "cu":29,  "zn":30,  "ga":31,  "ge":32,  "as":33,  "se":34,  "br":35,  "kr":36,\
                              "rb":37, "sr":38,  "y":39,   "zr":40,  "nb":41, "mo":42,  "tc":43,  "ru":44,  "rh":45,  "pd":46,  "ag":47,  "cd":48,  "in":49,  "sn":50,  "sb":51,  "te":52,  "i":53,   "xe":54,\
                              "cs":55, "ba":56,            "hf":72,  "ta":73, "w":74,   "re":75,  "os":76,  "ir":77,  "pt":78,  "au":79,  "hg":80,  "tl":81,  "pb":82,  "bi":83,  "po":84,  "at":85,  "rn":86}

        get_bonds.lone_e = {   'h':0, 'he':2,\
                              'li':0, 'be':2,                                                                                                                'b':0,     'c':0,     'n':2,     'o':4,     'f':6,    'ne':8,\
                              'na':0, 'mg':2,                                                                                                               'al':0,    'si':0,     'p':2,     's':4,    'cl':6,    'ar':8,\
                               'k':0, 'ca':2, 'sc':None, 'ti':None,  'v':None, 'cr':None, 'mn':None, 'fe':None, 'co':None, 'ni':None, 'cu':None, 'zn':None, 'ga':None, 'ge':0,    'as':3,    'se':4,    'br':6,    'kr':None,\
                              'rb':0, 'sr':2,  'y':None, 'zr':None, 'nb':None, 'mo':None, 'tc':None, 'ru':None, 'rh':None, 'pd':None, 'ag':None, 'cd':None, 'in':None, 'sn':None, 'sb':None, 'te':None,  'i':6,    'xe':None,\
                              'cs':0, 'ba':2, 'la':None, 'hf':None, 'ta':None,  'w':None, 're':None, 'os':None, 'ir':None, 'pt':None, 'au':None, 'hg':None, 'tl':None, 'pb':None, 'bi':None, 'po':None, 'at':None, 'rn':None  }

        # Initialize periodic table
        get_bonds.atomic_to_element = { get_bonds.periodic[i]:i for i in get_bonds.periodic.keys() }

    # Initalize atomic_number lists for use by the function
    atomic_number = [ get_bonds.periodic[i.lower()] for i in elements ]
    
    # Generate the bonding preference to optimally satisfy the valency conditions of each atom 
    bonding_pref = [ (count_i,get_bonds.sat_dict[i]) for count_i,i in enumerate(elements) ]

    # Convert to atomic numbers is working in elements mode
    atomtypes = [ "["+str(get_bonds.periodic[i.lower()])+"]" for i in elements ]

    # Initially assign all valence electrons as lone electrons
    lone_electrons    = np.zeros(len(atomtypes),dtype="int")    
    bonding_electrons = np.zeros(len(atomtypes),dtype="int")    
    core_electrons    = np.zeros(len(atomtypes),dtype="int")
    valence           = np.zeros(len(atomtypes),dtype="int")
    bonding_target    = np.zeros(len(atomtypes),dtype="int")
    for count_i,i in enumerate(atomtypes):

        # Grab the total number of (expected) electrons from the atomic number
        N_tot = int(i.split('[')[1].split(']')[0])

        # Determine the number of core/valence electrons based on row in the periodic table
        if N_tot > 54:
            print( "ERROR in get_bonds: the algorithm isn't compatible with atomic numbers greater than 54 owing to a lack of rules for treating lanthanides. Exiting...")
            quit()
        elif N_tot > 36:
            N_tot -= 36
            core_electrons[count_i] = 36
            valence[count_i]        = 18
        elif N_tot > 18:
            N_tot -= 18
            core_electrons[count_i] = 18
            valence[count_i]        = 18
        elif N_tot > 10:
            N_tot -= 10
            core_electrons[count_i] = 10
            valence[count_i]        = 8
        elif N_tot > 2:
            N_tot -= 2
            core_electrons[count_i] = 2
            valence[count_i]        = 8
        lone_electrons[count_i] = N_tot
        bonding_target[count_i] = N_tot - get_bonds.lone_e[get_bonds.atomic_to_element[int(i.split('[')[1].split(']')[0])]]    

    # Loop over the adjmat and assign initial bonded electrons assuming single bonds (and adjust lone electrons accordingly)
    for count_i,i in enumerate(adj_mat):
        bonding_electrons[count_i] += sum(i)
        lone_electrons[count_i] -= sum(i)

    # Eliminate all radicals by forming higher order bonds
    change_list = range(len(lone_electrons))
    outer_counter     = 0
    inner_max_cycles  = 1000
    outer_max_cycles  = 1000
    loop_list   = [ (atomic_number[i],i) for i in range(len(lone_electrons)) ]
    loop_list   = [ i[1] for i in sorted(loop_list) ]
    bonds_made = []
    bond_sat = False

    # Check for special chemical groups
    for i in range(len(atomtypes)):

        # Handle nitro groups
        if is_nitro(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ]
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],1)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            lone_electrons[O_ind[0]] += 1
            bonds_made += [(i,O_ind[1])]

        # Handle sulfoxide groups
        if is_sulfoxide(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfoxide atoms from the bonding_pref list
            bonding_pref += [(i,4)]
            bonding_pref += [(O_ind[0],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind[0])]

        # Handle sulfonyl groups
        if is_sulfonyl(i,adj_mat,elements) is True:
            O_ind = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] and sum(adj_mat[count_j]) == 1 ]
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the sulfonyl atoms from the bonding_pref list
            bonding_pref += [(i,6)]
            bonding_pref += [(O_ind[0],2)]
            bonding_pref += [(O_ind[1],2)]
            bonding_electrons[O_ind[0]] += 1
            bonding_electrons[O_ind[1]] += 1
            bonding_electrons[i] += 2
            lone_electrons[O_ind[0]] -= 1
            lone_electrons[O_ind[1]] -= 1
            lone_electrons[i] -= 2
            bonds_made += [(i,O_ind[0])]
            bonds_made += [(i,O_ind[1])]

        # Handle phosphate groups 
        if is_phosphate(i,adj_mat,elements) is True:
            O_ind      = [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and elements[count_j] in ["o","O"] ] # Index of single bonded O-P oxygens
            O_ind_term = [ j for j in O_ind if sum(adj_mat[j]) == 1 ] # Index of double bonded O-P oxygens
            bonding_pref = [ j for j in bonding_pref if j[0] != i and j[0] not in O_ind ] # remove bonds involving the phosphate atoms from the bonding_pref list
            bonding_pref += [(i,5)]
            bonding_pref += [(O_ind_term[0],2)] # during testing it ended up being important to only add a bonding_pref tuple for one of the terminal oxygens
            bonding_electrons[O_ind_term[0]] += 1
            bonding_electrons[i] += 1
            lone_electrons[O_ind_term[0]] -= 1
            lone_electrons[i] -= 1
            bonds_made += [(i,O_ind_term[0])]

    # diagnostic print            
    if verbose is True:
        print( "Starting electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # The outer loop checks each bonding structure produced by the inner loop for consistency with
    # the user specified "pref_bonding" and pref_argument with bonding electrons are
    while bond_sat is False:

        # Initialize necessary objects
        change_list   = range(len(lone_electrons))
        inner_counter = 0
        bond_sat = True
        random.shuffle(loop_list)
        
        # Inner loop forms bonds to remove radicals or underbonded atoms until no further
        # changes in the bonding pattern are observed.
        while len(change_list) > 0:
            change_list = []
            for i in loop_list:

                # List of atoms that already have a satisfactory binding configuration.
                happy = [ j[0] for j in bonding_pref if j[1] == bonding_electrons[j[0]]]            
                
                # If the current atom already has its target configuration then no further action is taken
                if i in happy: continue

                # If there are no lone electrons then skip
                if lone_electrons[i] == 0: continue

                # Take action if this atom has a radical or an unsatifisied bonding condition
                if lone_electrons[i] % 2 != 0 or bonding_electrons[i] != bonding_target[i]:

                    # Try to form a bond with a neighboring radical (valence +1/-1 check ensures that no improper 5-bonded atoms are formed)
                    bonded_radicals = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] % 2 != 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy ]
                    bonded_lonepairs = [ (atomic_number[count_j],count_j) for count_j,j in enumerate(adj_mat[i]) if j == 1 and lone_electrons[count_j] > 0 \
                                        and 2*(bonding_electrons[count_j]+1)+(lone_electrons[count_j]-1) <= valence[count_j] and lone_electrons[count_j]-1 >= 0 and count_j not in happy ]

                    # Sort by atomic number (cheap way of sorting carbon before other atoms, should probably switch over to electronegativities) 
                    bonded_radicals = [ j[1] for j in  sorted(bonded_radicals) ]
                    bonded_lonepairs = [ j[1] for j in  sorted(bonded_lonepairs) ]

                    # Correcting radicals is attempted first
                    if len(bonded_radicals) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_radicals[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_radicals[0]] -= 1
                        change_list += [i,bonded_radicals[0]]
                        bonds_made += [(i,bonded_radicals[0])]

                    # Else try to form a bond with a neighboring atom with spare lone electrons (valence check ensures that no improper 5-bonded atoms are formed)
                    elif len(bonded_lonepairs) > 0:
                        bonding_electrons[i] += 1
                        bonding_electrons[bonded_lonepairs[0]] += 1
                        lone_electrons[i] -= 1
                        lone_electrons[bonded_lonepairs[0]] -= 1
                        change_list += [i,bonded_lonepairs[0]]
                        bonds_made += [(i,bonded_lonepairs[0])]
            
            # Increment the counter and break if the maximum number of attempts have been made
            inner_counter += 1
            if inner_counter >= inner_max_cycles:
                print( "WARNING: maximum attempts to establish a reasonable lewis-structure exceeded ({}).".format(inner_max_cycles))

        # Check if the user specified preferred bond order has been achieved.
        if bonding_pref is not None:
            unhappy = [ i[0] for i in bonding_pref if i[1] != bonding_electrons[i[0]]]
            if len(unhappy) > 0:

                # Break the first bond involving one of the atoms bonded to the under/over coordinated atoms
                # NOTE: Added check since nitro-containing groups can lead to situations with no bonds being formed                
                ind = set([unhappy[0]] + [ count_i for count_i,i in enumerate(adj_mat[unhappy[0]]) if i == 1 ])

                # Check if a rearrangment is possible, break if none are available
                try:
                    break_bond = next( i for i in bonds_made if i[0] in ind or i[1] in ind )
                except:
                    print( "WARNING: no further bond rearrangments are possible and bonding_pref is still not satisfied.")
                    break

                # Perform bond rearrangment
                bonding_electrons[break_bond[0]] -= 1
                lone_electrons[break_bond[0]] += 1
                bonding_electrons[break_bond[1]] -= 1
                lone_electrons[break_bond[1]] += 1

                # Remove the bond from the list and reorder loop_list so that the indices involved in the bond are put last                
                bonds_made.remove(break_bond)
                loop_list.remove(break_bond[0])
                loop_list.remove(break_bond[1])
                loop_list += [break_bond[0],break_bond[1]]

                # Update the bond_sat flag
                bond_sat = False

            # Increment the counter and break if the maximum number of attempts have been made
            outer_counter += 1

            # Periodically reorder the list to avoid some cyclical walks
            if outer_counter % 100 == 0:
                loop_list = reorder_list(loop_list,atomic_number)

            # Print diagnostic upon failure
            if outer_counter >= outer_max_cycles:
                print( "WARNING: maximum attempts to establish a lewis-structure consistent")
                print( "         with the user supplied bonding preference has been exceeded ({}).".format(outer_max_cycles))
                break

    # diagnostic print            
    if verbose is True:
        print( "\nFinal electronic structure:")
        print( "\n{:40s} {:60} {:20} {:20} {:20} {}".format("elements","atomtypes","lone_electrons","bonding_electrons","core_electrons","bonded_atoms"))
        for count_i,i in enumerate(atomtypes):
            print( "{:40s} {:60} {:<20d} {:<20d} {:<20d} {}".format(elements[count_i],i,lone_electrons[count_i],bonding_electrons[count_i],core_electrons[count_i],",".join([ "{}".format(count_j) for count_j,j in enumerate(adj_mat[count_i]) if j == 1 ])))

    # Create the bond matrix
    bond_mat = adj_mat.copy()
    for i in bonds_made:
        bond_mat[i[0],i[1]] += 1
        bond_mat[i[1],i[0]] += 1

    return bond_mat

# Helper function to check_lewis and get_bonds that rolls the loop_list carbon elements
def reorder_list(loop_list,atomic_number):
    c_types = [ count_i for count_i,i in enumerate(loop_list) if atomic_number[i] == 6 ]
    others  = [ count_i for count_i,i in enumerate(loop_list) if atomic_number[i] != 6 ]
    if len(c_types) > 1:
        c_types = c_types + [c_types.pop(0)]
    return [ loop_list[i] for i in c_types+others ]

# Returns a matrix of graphical separations for all nodes in a graph defined by the inputted adjacency matrix 
def graph_seps(adj_mat_0):

    # Create a new name for the object holding A**(N), initialized with A**(1)
    adj_mat = deepcopy(adj_mat_0)
    
    # Initialize an np.array to hold the graphical separations with -1 for all unassigned elements and 0 for the diagonal.
    seps = np.ones([len(adj_mat),len(adj_mat)])*-1
    np.fill_diagonal(seps,0)

    # Perform searches out to len(adj_mat) bonds (maximum distance for a graph with len(adj_mat) nodes
    for i in np.arange(len(adj_mat)):        

        # All perform assignments to unassigned elements (seps==-1) 
        # and all perform an assignment if the value in the adj_mat is > 0        
        seps[np.where((seps==-1)&(adj_mat>0))] = i+1

        # Since we only care about the leading edge of the search and not the actual number of paths at higher orders, we can 
        # set the larger than 1 values to 1. This ensures numerical stability for larger adjacency matrices.
        adj_mat[np.where(adj_mat>1)] = 1
        
        # Break once all of the elements have been assigned
        if -1 not in seps:
            break

        # Take the inner product of the A**(i+1) with A**(1)
        adj_mat = np.dot(adj_mat,adj_mat_0)

    return seps

# # Returns a matrix of graphical separations for all nodes in a graph defined by the inputted adjacency matrix 
# # OLD FUNCTION HAD PROBLEMS WITH LARGE ADJACENCY MATRICES
# def graph_seps(adj_mat_0):

#     # Create a new name for the object holding A**(N), initialized with A**(1)
#     adj_mat = adj_mat_0
    
#     # Initialize an np.array to hold the graphical separations with -1 for all unassigned elements and 0 for the diagonal.
#     seps = np.ones([len(adj_mat),len(adj_mat)])*-1
#     np.fill_diagonal(seps,0)

#     # Perform searches out to len(adj_mat) bonds (maximum distance for a graph with len(adj_mat) nodes
#     for i in np.arange(len(adj_mat)):        

#         # All perform assignments to unassigned elements (seps==-1) 
#         # and all perform an assignment if the value in the adj_mat is > 0
#         seps[np.where((seps==-1)&(adj_mat>0))] = i+1

#         # Break once all of the elements have been assigned
#         if -1 not in seps:
#             break

#         # Take the inner product of the A**(i+1) with A**(1)
#         adj_mat = np.dot(adj_mat,adj_mat_0)

#     # Return the graphical separations
#     return seps

# Returns the set of connected nodes to the start node, while avoiding any connections through nodes in the avoid list. 
def return_connected(adj_mat,start=0,avoid=[]):

    # Initialize the avoid list with the starting index
    avoid = set(avoid+[start])

    # new_0 holds the most recently encountered nodes, beginning with start
    # new_1 is a set holding all of the encountered nodes
    new_0 = [start]
    new_1 = set([start])

    # keep looping until no new nodes are encountered
    while len(new_0) > 0:        

        # reinitialize new_0 with new connections
        new_0 = [ count_j for i in new_0 for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j not in avoid ]

        # update the new_1 set and avoid list with the most recently encountered new nodes
        new_1.update(new_0)
        avoid.update(new_0)

    # return the set of encountered nodes
    return new_1

# Returns the list of terminal centers, where a terminal center is an atom with only one 
# bond to a non-terminal atom.
def terminal_centers(adj_mat):    
    return [ count_i for count_i,i in enumerate(adj_mat) if sum(i) > 1 and len([ j for count_j,j in enumerate(i) if j == 1 and sum(adj_mat[count_j]) > 1 ]) == 1 ]

# This function generates a local adjacency matrix from an atomtype label
def type_adjmat(label):

    # Initialize breaks (indices for brackets in "label"), atoms (start:end index tuples for the atom labels),
    # labels ( basis of atom labels indexed to the adjmat), and adj_mat (the local adjacency matrix with connectivity relationships)
    breaks = [ count_i for count_i,i in enumerate(label) if i in ['[',']','=','#'] ]  
    atoms  = [ (i+1,i+breaks[count_i+1]-i) for count_i,i in enumerate(breaks[:-1]) if breaks[count_i+1]-i > 1 ]    
    labels = [ label[i[0]:i[1]] for i in atoms ]   
    adj_mat = np.zeros([len(atoms),len(atoms)])      
    
    # Loop over atoms
    for count_i,i in enumerate(atoms):

        # Initialize variables
        starting_index = breaks.index(i[1])       # index of the nearest bracket forward from the current atom label
        break_count=0                             # counter for keeping track of who needs parsing and who is connected to who

        # Loop over brackets
        for count_j,j in enumerate(breaks[starting_index:-1]):

            # Increment break_count + 1 for "open" brackets
            if label[j] == "[": break_count += 1

            # Increment break_count - 1 for "closed" brackets
            if label[j] == "]": break_count -= 1

            # If the break_count variable is -1 then all connections have been found
            if break_count == -1:
                break

            # When break_count == 1 and the parser resides at an open bracket, the next atom past the bracket is connected
            if break_count == 1 and label[j] == "[":
                idx = next( count_k for count_k,k in enumerate(atoms) if k[0] == j+1 )
                adj_mat[count_i,idx] = 1
                adj_mat[idx,count_i] = 1

    return adj_mat, labels


# Description:
# Rotate Point by an angle, theta, about the vector with an orientation of v1 passing through v2. 
# Performs counter-clockwise rotations (i.e., if the direction vector were pointing
# at the spectator, the rotations would appear counter-clockwise)
# For example, a 90 degree rotation of a 0,0,1 about the canonical 
# y-axis results in 1,0,0.
#
# Point: 1x3 np.array, coordinates to be rotated
# v1: 1x3 np.array, point the rotation passes through
# v2: 1x3 np.array, rotation direction vector
# theta: scalar, magnitude of the rotation (defined by default in degrees)
def axis_rot(Point,v1,v2,theta,mode='angle'):

    # Temporary variable for performing the transformation
    rotated=np.array([Point[0],Point[1],Point[2]])

    # If mode is set to 'angle' then theta needs to be converted to radians to be compatible with the
    # definition of the rotation vectors
    if mode == 'angle':
        theta = theta*np.pi/180.0

    # Rotation carried out using formulae defined here (11/22/13) http://inside.mines.edu/fs_home/gmurray/ArbitraryAxisRotation/)
    # Adapted for the assumption that v1 is the direction vector and v2 is a point that v1 passes through
    a = v2[0]
    b = v2[1]
    c = v2[2]
    u = v1[0]
    v = v1[1]
    w = v1[2]
    L = u**2 + v**2 + w**2

    # Rotate Point
    x=rotated[0]
    y=rotated[1]
    z=rotated[2]

    # x-transformation
    rotated[0] = ( a * ( v**2 + w**2 ) - u*(b*v + c*w - u*x - v*y - w*z) )\
             * ( 1.0 - np.cos(theta) ) + L*x*np.cos(theta) + L**(0.5)*( -c*v + b*w - w*y + v*z )*np.sin(theta)

    # y-transformation
    rotated[1] = ( b * ( u**2 + w**2 ) - v*(a*u + c*w - u*x - v*y - w*z) )\
             * ( 1.0 - np.cos(theta) ) + L*y*np.cos(theta) + L**(0.5)*(  c*u - a*w + w*x - u*z )*np.sin(theta)

    # z-transformation
    rotated[2] = ( c * ( u**2 + v**2 ) - w*(a*u + b*v - u*x - v*y - w*z) )\
             * ( 1.0 - np.cos(theta) ) + L*z*np.cos(theta) + L**(0.5)*( -b*u + a*v - v*x + u*y )*np.sin(theta)

    rotated = rotated/L
    return rotated


# Description: finds the number of disconnected subnetworks in the 
#              adjacency matrix, which corresponds to the number of 
#              separate molecules.
#
# Inputs:      adj_mat: numpy np.array holding a 1 in the indices of bonded
#                        atom types. 
#
# Returns:     mol_count: scalar, the number of molecules in the adj_mat
def mol_count(adj_mat):
    
    # Initialize list of atoms assigned to molecules and a counter for molecules
    placed_idx = []    
    mol_count = 0

    # Continue the search until all the atoms have been assigned to molecules
    while len(placed_idx)<len(adj_mat):

        # Use sequential elements of the adj_mat as seeds for the spanning network search
        for count_i,i in enumerate(adj_mat):

            # Only proceed with search if the current atom hasn't been placed in a molecule
            if count_i not in placed_idx:

                # Increment mol_count for every new seed and add the seed to the list of placed atoms
                mol_count += 1               
                placed_idx += [count_i]
                
                # Find connections
                idx = [ count_j for count_j,j in enumerate(i) if j==1 and count_j not in placed_idx ]
                
                # Continue until no new atoms are found
                while len(idx) > 0:
                    current = idx.pop(0)
                    if current not in placed_idx:
                        placed_idx += [current]
                        idx += [ count_k for count_k,k in enumerate(adj_mat[current]) if k == 1 and count_k not in placed_idx ]
    return mol_count

# Description: finds the distance from a terminus for each node in the adjacency matrix
#
# Inputs:      adj_mat: an adjacency matrix of the system
#
# Returns:     distance: a list, indexed to the adjacency matrix of the graphical distance
#                        from a terminus for all nodes in the adjacency matrix.
def terminal_dist(adj_mat):

    dists   = [ None for i in range(len(adj_mat)) ]
    current = set([ count_i for count_i,i in enumerate(adj_mat) if sum(i) <= 1 ])
    gen     = 0
    while None in dists:
        next = []
        for i in current:
            dists[i]  = gen
            next     += [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and dists[count_j] is None and count_j not in current ]
        current = set(next)
        gen += 1
    return dists

# Description: finds the nesting depth of each node in a network. The nesting depth is defined as the number
#              of terminal node generations that need to be removed from a network before a given node is itself
#              a terminal node. This metric is used to determine the order in which atomtypes need to be
#              paramtrized for VDW fitting. 
#
# Inputs:      adj_mat: an adjacency matrix of the system
#
# Returns:     nesting: a list, indexed to the adjacency matrix of the graphical distance
#                       from a terminus for all nodes in the adjacency matrix.
def nesting_depth(adj_mat):

    depths   = [ None for i in range(len(adj_mat)) ]
    ind      = range(len(adj_mat))
    gen      = 0
    while None in depths:
        unassigned = range(len(adj_mat))
        for count_i,i in enumerate(adj_mat):
            if sum(i) <= 1:
                depths[ind[count_i]] = gen
                unassigned.remove(count_i)
        gen     += 1
        adj_mat  = adj_mat[unassigned,:][:,unassigned]
        ind      = [ ind[i] for i in unassigned ]

    return depths

# Description: Returns the canonical fragment corresponding to the mode defined associated with geo and atoms m_ind.
#
# Inputs:      m_ind:        list of indices involved in the mode
#              geo:          an Nx3 np.array holding the geometry of the molecule
#              adj_mat:      an NxN np.array holding the connectivity of the molecule
#              gens:         an integer specifying the number of generations involved in the geometry search
#                            (Algorithm returns 
#              force_linear: boolean, forces a non-cyclic structure.
#
# Returns:     m_ind:        list of indices involved in the mode (in terms of the new geometry)
#              N_geo:        new geometry for parameterizing the mode.
#              N_adj_mat:    new adjacency matrix
#              N_dup:        user supplied lists indexed to the original geometry, now indexed to the new geometry
def mode_geo(m_ind,geo,adj_mat,gens=2,dup=[],force_linear=False):

    from transify import transify
    
    # Seed conditions for...
    # atoms: single atom
    # bonds: both atoms
    # angles: center atom
    # linear dihedral: center atoms
    # improper dihedral: center atom
    # b_top: holds the topology of the mode, only used for remapping when using the force_linear algorithm
    m_ind_0 = deepcopy(m_ind)                # A copy is made to assign the mode index at the end
    if len(m_ind) == 1 or len(m_ind) == 2:        
        m_ind = m_ind
        b_top = [[]]
    elif len(m_ind) == 2:
        m_ind = m_ind
        b_top = [[1],[0]]
    elif len(m_ind) == 3:
        m_ind = [m_ind[1]]
        b_top = [[1],[0,2],[1]]
    elif len(m_ind) == 4:
        # Check for linear condition (a bond between the center atoms)
        if adj_mat[m_ind[1],m_ind[2]] == 1 and adj_mat[m_ind[2],m_ind[3]] == 1:
            m_ind = [m_ind[1],m_ind[2]]
            b_top = [[1],[0,2],[1,3],[2]]
            force_linear = True

        # Treat it as an improper
        else:
            m_ind = [m_ind[0]]
            b_top = [[1,2,3],[0],[0],[0]]
    #
    # Creates a non-linear but constitutionally identical topology. For linear structures there is no difference between the if/else statements
    #
    if force_linear is True:

        new_atoms  = []
        bonds = [ (m_ind.index(i),m_ind.index(count_j)) for i in m_ind for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j in m_ind ]  # holds the bonds in the new adj mat
        parent_next = [ [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j in m_ind ] for i in m_ind ] # holds the "parents" of each added atom to avoid backtracking
        for i in range(gens+1):

            # Used for indexing the bonds
            current_length = len(new_atoms)

            # Update the atoms that are included in the geometry (new_atoms) 
            # as well as the connections that need to be iterated over (cons)
            # on the first generation the cons are seeded with m_ind
            if i == 0:
                new_atoms += m_ind
                cons  = m_ind
            else:
                new_atoms += cons_next
                cons  = cons_next

            # Exits after adding the final generation of connections
            if i == gens:
                break

            # Refresh the parent and "origin" lists. "origin" is different from parent because it
            # stores the index in new_atoms of each node in cons, this is needed for properly indexing the bonds.
            parent = parent_next     
            cons_next = []
            parent_next = []
            origins = [ current_length+j for j in range(len(cons)) ]

            # Loop over the connections at the current generation, find the next generation of
            # connections and avoid backtracking. 
            for count_j,j in enumerate(cons):
                for count_k,k in enumerate(adj_mat[j]):
                    if k == 1 and count_k not in parent[count_j]:
                        cons_next  += [count_k]
                        bonds += [ (origins[count_j],len(new_atoms) + len(cons_next) - 1) ]
                        parent_next += [[j]]

        # Generate the new adjacency matrix
        N_adj_mat = np.zeros([len(new_atoms),len(new_atoms)])
        for i in bonds:
            N_adj_mat[i[0],i[1]] = 1
            N_adj_mat[i[1],i[0]] = 1            

    #
    # Use graph_seps algorithm: keeps all atoms and the topology out to gens bonds
    #
    else:

        # Graphical separations are used for determining which atoms and bonds to keep
        gs = graph_seps(adj_mat)    

        # all atoms within "gens" of the m_ind atoms are kept
        # all bonds within "gens" of the m_ind atoms are kept (i.e. bonds between the "gens" separated atoms are NOT kept
        new_atoms = list(set([ count_j for i in m_ind for count_j,j in enumerate(gs[i]) if j <= gens ]))
        N_adj_mat = adj_mat[new_atoms,:][:,new_atoms]

        # remove the bonds between the "gens" separated atoms    
        edge_ind = list(set([ count_j for i in m_ind for count_j,j in enumerate(gs[i]) if j == gens ]))
        edge_ind = [ new_atoms.index(i) for i in edge_ind if min([ gs[j,i] for j in m_ind ]) == gens ]
        for i in edge_ind:
            for j in edge_ind:
                N_adj_mat[i,j] = 0
                N_adj_mat[j,i] = 0

    # Create the new geometry and adj_mat
    N_geo     = np.zeros([len(new_atoms),3])
    for count_i,i in enumerate(new_atoms):
        N_geo[count_i,:] = geo[i,:]

    # Duplicate the respective lists
    N_dup = {}
    for count_i,i in enumerate(dup):
        N_dup[count_i] = []
        for j in new_atoms:
            N_dup[count_i] += [i[j]]
    N_dup = [ N_dup[i] for i in range(len(N_dup.keys())) ]

    # Clean up the geometry
    N_geo = transify(N_geo,N_adj_mat,opt_terminals=False,opt_final=False)            

    # Assign the mode ind 
    # NOTE: the use of the list.index() method assumes that the mode indices are the first occuring in the geometry
    #       this should be a very good assumption for all conventional modes and seed scenarios (no exceptions have been found).
    if force_linear is True:
        
        # A more complicated remap is required for the force_linear algorithm because care needs to be 
        # taken to ensure that the essential topology of m_ind_0 is preserved.

        # inds holds the mapped m_ind and it is initially seeded with the either 
        # "None" values or the values from m_ind_0 that seeded the mode search
        inds = [ None if i not in m_ind else new_atoms.index(i) for i in m_ind_0 ]

        # calculate the values for inds that preserve the original topology of m_ind
        for count_i,i in enumerate(inds):

            # Skip if already assigned
            if i is not None:
                continue
                
            # Find the indices in the old adjacency matrix for which m_ind_0[count_i] had connections with other m_ind_0 atoms.
            must_be_connected_to_old = [ count_j for count_j,j in enumerate(adj_mat[m_ind_0[count_i]]) if j == 1 and  count_j in m_ind_0 ]

            # Find connections in inds that have already been placed and must be presereved for assigning inds[count_i]
            must_be_connected_to_new = [ inds[j] for j in b_top[count_i] if inds[j] is not None ]

            # Find all of the atoms that have the right originating index
            candidates = [ count_j for count_j,j in enumerate(new_atoms) if j == m_ind_0[count_i] ] 
            for j in candidates:

                # Check if the candidate j has the right connections in terms of 
                # (i) the atom types it is connected to and
                # (ii) connections with respect to atoms in inds that have already been assigned
                connections = [ new_atoms[count_k] for count_k,k in enumerate(N_adj_mat[j]) if k == 1 ]
                if False not in [ k in connections for k in must_be_connected_to_old ] and False not in [ N_adj_mat[j,k] == 1 for k in must_be_connected_to_new ]:
                    inds[count_i] =  j
                    break

        # Assign the mapping
        m_ind = inds

    else:
        m_ind = [ new_atoms.index(i) for i in m_ind_0 ]

    return m_ind,N_geo,N_adj_mat,N_dup

def new_mode_geo(m_ind,geo,adj_mat,bond_mat,gens=2,dup=[],force_linear=False):
    
    m_ind_0 = deepcopy(m_ind)
    from transify import transify
    # Seed conditions for...
    # atoms: single atom
    # bonds: both atoms
    # angles: center atom
    # linear dihedral: center atoms
    # improper dihedral: center atom
    # b_top: holds the topology of the mode (which atoms are bonded to which), only used for remapping when using the force_linear algorithm
    if len(m_ind) == 1 or len(m_ind) == 2:        
        m_ind = m_ind
        b_top = [[]]
    elif len(m_ind) == 2:  # XXX why is this here? 7/10/20
        m_ind = m_ind
        b_top = [[1],[0]]
    elif len(m_ind) == 3:
        m_ind = [m_ind[1]]
        b_top = [[1],[0,2],[1]]
    elif len(m_ind) == 4:
        # Check for linear condition (a bond between the center atoms)
        if adj_mat[m_ind[1],m_ind[2]] == 1 and adj_mat[m_ind[2],m_ind[3]] == 1:
            m_ind = [m_ind[1],m_ind[2]]
            b_top = [[1],[0,2],[1,3],[2]]
            force_linear = True

        # Treat it as an improper
        else:
            m_ind = [m_ind[0]]
            b_top = [[1,2,3],[0],[0],[0]]
    #
    # Creates a non-linear but constitutionally identical topology. For linear structures there is no difference between the if/else statements
    #
    if force_linear is True:

        new_atoms  = []
        bonds = [ (m_ind.index(i),m_ind.index(count_j)) for i in m_ind for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j in m_ind ]  # holds the bonds in the new adj mat
        original_bonds = [ (i,count_j) for i in m_ind for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j in m_ind ] # holds the original bonds in the new adj mat
        parent_next = [ [ count_j for count_j,j in enumerate(adj_mat[i]) if j == 1 and count_j in m_ind ] for i in m_ind ] # holds the "parents" of each added atom to avoid backtracking
        for i in range(gens+1):
            
            # Used for indexing the bonds
            current_length = len(new_atoms)

            # Update the atoms that are included in the geometry (new_atoms) 
            # as well as the connections that need to be iterated over (cons)
            # on the first generation the cons are seeded with m_ind
            if i == 0:
                new_atoms += m_ind
                cons  = m_ind
            else:
                new_atoms += cons_next
                cons  = cons_next

            # Exits after adding the final generation of connections
            if i == gens:
                break

            # Refresh the parent and "origin" lists. "origin" is different from parent because it
            # stores the index in new_atoms of each node in cons, this is needed for properly indexing the bonds.
            parent = parent_next     
            cons_next = []
            parent_next = []
            origins = [ current_length+j for j in range(len(cons)) ]

            # Loop over the connections at the current generation, find the next generation of
            # connections and avoid backtracking. 
            for count_j,j in enumerate(cons):
                for count_k,k in enumerate(adj_mat[j]):
                    if k == 1 and count_k not in parent[count_j]:
                        cons_next  += [count_k]
                        bonds += [ (origins[count_j],len(new_atoms) + len(cons_next) - 1) ]
                        original_bonds += [ (j,count_k) ]
                        parent_next += [[j]]

        # Generate the new adjacency matrix
        N_adj_mat = np.zeros([len(new_atoms),len(new_atoms)])

        # determine single or multiple bond_mats
        if len(bond_mat) > 0 and len(bond_mat) != len(geo): # multuple bond_mats
            N_bond_mats = []
            for count_i,i in enumerate(bonds):
                N_adj_mat[i[0],i[1]] = 1
                N_adj_mat[i[1],i[0]] = 1

            for lb in range(len(bond_mat)):
                N_bond_mat = np.zeros([len(new_atoms),len(new_atoms)]) 
                for count_i,i in enumerate(bonds):
                    N_bond_mat[i[0],i[1]]= bond_mat[lb][original_bonds[count_i][0],original_bonds[count_i][1]]
                    N_bond_mat[i[1],i[0]]= bond_mat[lb][original_bonds[count_i][0],original_bonds[count_i][1]]
                N_bond_mats += [N_bond_mat]
        else:
            N_bond_mat =np.zeros([len(new_atoms),len(new_atoms)]) 
            for count_i,i in enumerate(bonds):
                N_adj_mat[i[0],i[1]] = 1
                N_adj_mat[i[1],i[0]] = 1
                N_bond_mat[i[0],i[1]]= bond_mat[original_bonds[count_i][0],original_bonds[count_i][1]]
                N_bond_mat[i[1],i[0]]= bond_mat[original_bonds[count_i][0],original_bonds[count_i][1]]
            
    #
    # Use graph_seps algorithm: keeps all atoms and the topology out to gens bonds
    #
    else:

        # Graphical separations are used for determining which atoms and bonds to keep
        gs = graph_seps(adj_mat)    
        # all atoms within "gens" of the m_ind atoms are kept
        # all bonds within "gens" of the m_ind atoms are kept (i.e. bonds between the "gens" separated atoms are NOT kept
        new_atoms = list(set([ count_j for i in m_ind for count_j,j in enumerate(gs[i]) if j <= gens ]))
        N_adj_mat = adj_mat[new_atoms,:][:,new_atoms]
        # determine single or multiple bond_mats
        if len(bond_mat) > 0 and len(bond_mat) != len(geo): # multuple bond_mats 
            N_bond_mats = []
            for lb in range(len(bond_mat)):
                N_bond_mat = bond_mat[lb][new_atoms,:][:,new_atoms] 
                N_bond_mats += [N_bond_mat] 
        else:
            N_bond_mat = bond_mat[new_atoms,:][:,new_atoms]
            
        # remove the bonds between the "gens" separated atoms    
        edge_ind = list(set([ count_j for i in m_ind for count_j,j in enumerate(gs[i]) if j == gens ]))
        edge_ind = [ new_atoms.index(i) for i in edge_ind if min([ gs[j,i] for j in m_ind ]) == gens ]
        for i in edge_ind:
            for j in edge_ind:
                N_adj_mat[i,j] = 0
                N_adj_mat[j,i] = 0
                N_bond_mat[i,j] = 0
                N_bond_mat[j,i] = 0

    # Create the new geometry and adj_mat
    N_geo     = np.zeros([len(new_atoms),3])
    for count_i,i in enumerate(new_atoms):
        N_geo[count_i,:] = geo[i,:]
    
    # Duplicate the respective lists
    N_dup = {}
    for count_i,i in enumerate(dup):
        N_dup[count_i] = []
        for j in new_atoms:
            N_dup[count_i] += [i[j]]
    N_dup = [ N_dup[i] for i in range(len(N_dup.keys())) ]

    # Clean up the geometry
    N_geo = transify(N_geo,N_adj_mat,opt_terminals=False,opt_final=False)            

    # Assign the mode ind 
    # NOTE: the use of the list.index() method assumes that the mode indices are the first occuring in the geometry
    #       this should be a very good assumption for all conventional modes and seed scenarios (no exceptions have been found).
    if force_linear is True:
        
        # A more complicated remap is required for the force_linear algorithm because care needs to be 
        # taken to ensure that the essential topology of m_ind_0 is preserved.

        # inds holds the mapped m_ind and it is initially seeded with the either 
        # "None" values or the values from m_ind_0 that seeded the mode search
        inds = [ None if i not in m_ind else new_atoms.index(i) for i in m_ind_0 ]

        # calculate the values for inds that preserve the original topology of m_ind
        for count_i,i in enumerate(inds):

            # Skip if already assigned
            if i is not None:
                continue
                
            # Find the indices in the old adjacency matrix for which m_ind_0[count_i] had connections with other m_ind_0 atoms.
            must_be_connected_to_old = [ count_j for count_j,j in enumerate(adj_mat[m_ind_0[count_i]]) if j == 1 and  count_j in m_ind_0 ]

            # Find connections in inds that have already been placed and must be presereved for assigning inds[count_i]
            must_be_connected_to_new = [ inds[j] for j in b_top[count_i] if inds[j] is not None ]

            # Find all of the atoms that have the right originating index
            candidates = [ count_j for count_j,j in enumerate(new_atoms) if j == m_ind_0[count_i] ] 
            for j in candidates:

                # Check if the candidate j has the right connections in terms of 
                # (i) the atom types it is connected to and
                # (ii) connections with respect to atoms in inds that have already been assigned
                connections = [ new_atoms[count_k] for count_k,k in enumerate(N_adj_mat[j]) if k == 1 ]
                if False not in [ k in connections for k in must_be_connected_to_old ] and False not in [ N_adj_mat[j,k] == 1 for k in must_be_connected_to_new ]:
                    inds[count_i] =  j
                    break

        # Assign the mapping
        m_ind = inds

    else:
        m_ind = [ new_atoms.index(i) for i in m_ind_0 ]

    if len(bond_mat) > 0 and len(bond_mat) != len(geo): # multuple bond_mats
        return m_ind,N_geo,N_adj_mat,N_bond_mats,N_dup
    else:
        return m_ind,N_geo,N_adj_mat,N_bond_mat,N_dup

def read_alljson(jsonfile):
    if os.path.isfile(jsonfile) is False:
      print("Error: json file: {} not found".format(jsonfile))
      quit()
    obj_text = codecs.open(jsonfile, 'r').read()
    jload = json.loads(obj_text)
    
    return jload
