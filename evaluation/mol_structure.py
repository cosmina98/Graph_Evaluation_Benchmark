import rdkit
from rdkit import Chem
from rdkit.Chem.rdchem import ChiralType, BondType, BondDir
import enum
from rdkit.Chem.rdmolops import AddHs
import networkx as nx
import matplotlib
from networkx.drawing.nx_agraph import graphviz_layout,pygraphviz_layout
from pylab import rcParams
import matplotlib as mpl
from matplotlib import pyplot as plt
import random
import numpy as np
from colour import Color
import os 
import sys
from .atom_bond_encoder import  atom_to_feature_vector,bond_to_feature_vector
current = os.getcwd()
parent = os.path.dirname(current)
sys.path.append(parent)

#for zinc


"""
def get_dict_of_nodes():
    dict_of_nodes={0: 'C', 1: 'O',2: 'N',3: 'F',4: 'C',5: 'S', 6: 'Cl', 7: 'O', 8: 'N',9: 'Br', 10: 'N', 11: 'N', 12: 'N', 13: 'N', 14: 'S ', 15: 'I', 16: 'P', 17: 'O', 18: 'N', 19: 'O',20: 'S', 21: 'P' ,22: 'P',23: 'C', 24: 'P',25: 'S',26: 'C',27: 'P'}
    return dict_of_nodes
    
def get_atomic_number():
    dict_of_atomic_no ={ 'C':6, 'O':8, 'N':7, 'F':9, 'S':16, 'Cl':17,  'Br':35, 'I':53, 'P':15}
    return dict_of_atomic_no
"""

def foo(g):
  
    nx.draw(g)
    Draw.MolToMPL(nx_to_mol(g))
   
    return None


def rdkmol_to_nx(mol):
    #  rdkit-mol object to nx.graph
    graph = nx.Graph()
    for atom in mol.GetAtoms():
        graph.add_node(atom.GetIdx(), label=int(atom.GetAtomicNum()), attr=atom_to_feature_vector(atom) ,  label_name=atom.GetSymbol())
    for bond in mol.GetBonds():
        graph.add_edge(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx(),label=(int(bond.GetBondTypeAsDouble())),
                       attr=bond_to_feature_vector(bond),
                       edge_label=str(bond.GetBondType()) )
    return graph



def list_of_smiles_to_nx_graphs(smiles):
    list_of_nx_graphs=[]
    for i,smile in enumerate(smiles):
        mol = Chem.MolFromSmiles(smile)
        if mol:
           list_of_nx_graphs.append(rdkmol_to_nx(mol))
        else:
           # print('Check smile entry no', i+1)
            list_of_nx_graphs.append(rdkmol_to_nx(Chem.MolFromSmiles('C')))
         
    return list_of_nx_graphs

def nx_to_rdkit(graph):
    m = Chem.MolFromSmiles('')
    mw = Chem.RWMol(m)
    atom_index = {}
    for n, d in graph.nodes(data=True):
        atom_index[n] = mw.AddAtom(Chem.Atom(d['label']))
    for a, b, d in graph.edges(data=True):
        start = atom_index[a]
        end = atom_index[b] 
        try:
            mw.AddBond(start, end, eval("rdkit.Chem.rdchem.BondType.{}".format(bond_type)))
        except:
            #print('exc',bond_type)
            continue
            raise Exception('bond type not implemented')

    mol = mw.GetMol()
    return mol


def list_of_nx_graphs_to_smiles(graphs, file=None):
    # writes smiles strings to a file
    chem = [nx_to_rdkit(graph) for graph in graphs]
    smis = [Chem.MolToSmiles(m) for m in chem]
    if file:
        with open(file, 'w') as f:
            f.write('\n'.join(smis))
    return smis



def Hex_color(bond_type):
    random.seed( np.sum([ord(c) for c in bond_type]) -30+ ord(bond_type[0]))
    L = '0123456789ABCDEF'
    x= Color('#'+ ''.join([random.choice(L) for i in range(6)][:]))
    return x.get_hex()

def get_edge_color_list(mol_nx):
    edge_color=[ Hex_color(data[2]) for data in mol_nx.edges(data = 'edge_label')] 
    #print(edge_color)
    return edge_color

def return_colors_for_atoms(mol_nx):
    random.seed(767)
    color_map = {}
    for idx in mol_nx.nodes():
      if mol_nx.nodes[idx]['label_name'] not in color_map:
          color_map[mol_nx.nodes[idx]['label_name']] ="#%06x" % random.randint(sum([ord(c) for c in mol_nx.nodes[idx]['label']]), 0xFFFFFF) 
    mol_colors = []
    for idx in mol_nx.nodes():
        if (mol_nx.nodes[idx]['label_name'] in color_map):
            mol_colors.append(color_map[mol_nx.nodes[idx]['label_name']])
        else:
            mol_colors.append('gray')
    return mol_colors

def get_labels(mol_nx):
    return nx.get_node_attributes(mol_nx, 'label_name')
#set(nx.get_node_attributes(mol_nx, 'atom_symbol').values())
#colors=[i/len(mol_nx.nodes) for i in range(len(mol_nx.nodes))]

def draw_one_mol(G, ax=None):
    rcParams['figure.figsize'] = 7.5,5
    #color_lookup = {k:v for v, k in enumerate(sorted((nx.get_node_attributes(G, "atom_symbol"))))}
    selected_data = dict( (n, ord(d['label_name'][0])**3 ) for n,d in G.nodes().items() )
    selected_data=[v[1] for k, v in enumerate(selected_data.items())]
    low, *_, high = sorted(selected_data)
    seed=123
    random.seed(seed)
    np.random.seed(seed)    
    pos=pygraphviz_layout(G)
    nx.draw_networkx_nodes(G,pos,
            #labels= get_labels(G),
            node_size=100,
            #edgecolors='black',
            cmap='tab20c_r',
            vmin=low,
            vmax=high,
            node_color=[selected_data],
            ax=ax)
    nx.draw_networkx_labels(G,pos, get_labels(G),ax=ax)
    nx.draw_networkx_edges(G, pos,
          
            width=3,
            edge_color=get_edge_color_list(G),
         ax=ax)
    #nx.draw_networkx_edge_labels(G, pos, get_edge_labels(G), font_size=10,alpha=0.8,verticalalignment='bottom',
                                #horizontalalignment='center',clip_on='True',rotate='True' )
   


def get_edge_labels(G):
  return nx.get_edge_attributes(G,'edge_label')
   
def get_adjency_matrix(mol_nx):
    # print out the adjacency matrix ---------------------------------------------- 
    matrix = nx.to_numpy_matrix(mol_nx)
    print(matrix)
    return matrix



def draw_graphs(list_of_graph_molecules, num_per_line=3,labels=None):
      ixs=[]
      num_per_line_ax_n=0
      if len(list_of_graph_molecules)%num_per_line==0:
       lines=int(len(list_of_graph_molecules)/num_per_line)
      else:
        lines=len(list_of_graph_molecules)//num_per_line+1
        num_per_line_ax_n=len(list_of_graph_molecules) % num_per_line
        for i in range(num_per_line-num_per_line_ax_n):
          ix=lines-1,num_per_line-i-1
          ixs.append(ix)
          
      #print(lines)
      fig, ax = plt.subplots(lines, num_per_line)
      fig.set_figheight(10)
      fig.set_figwidth(15)
      for i, mol_nx in enumerate(list_of_graph_molecules):
        ix = np.unravel_index(i, ax.shape)
        draw_one_mol(mol_nx, ax=ax[ix])
        if labels is not None:
            ax[ix].set_title(labels[i], fontsize=8)
      for ix in ixs:
           ax[ix].set_axis_off()
 