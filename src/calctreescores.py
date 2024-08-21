import json
import treescore
import pandas as pd
import toytree
import numpy as np
from scipy.stats import describe
import copy


#calc the taxscore 
uniprot_df = pd.read_csv(snakemake.input[0])
scores = {}
stats = {}

for t in snakemake.input[1:]:
    tree = toytree.tree(t )
    lineages = treescore.make_lineages(uniprot_df)
    species = treescore.get_species(tree.treenode)
    tree = treescore.label_leaves( tree , lineages)
    #tree = treescore.labelwRED(tree.treenode)
    overlap = treescore.getTaxOverlap(tree.treenode)
    taxscore = tree.treenode.score
    
    #calc descriptive stats on normalized branch lens to see if trees are balanced  
    lengths = np.array([node.dist for node in tree.treenode.traverse()])
    lengths /= np.sum(lengths)
    #calc the root first taxscore
    
    tree1 = copy.deepcopy(tree)
    degree_score1 = treescore.degree_score(tree1.treenode, exp = 1  )
    
    tree2 = copy.deepcopy(tree)
    degree_score15 = treescore.degree_score(tree2.treenode , exp = 1.5 )

    tree3 = copy.deepcopy(tree)
    degree_score2 = treescore.degree_score(tree3.treenode , exp = 2 )

    tree4 = copy.deepcopy(tree)
    treescore.getTaxOverlap_root(tree4.treenode)
    root_score , root_score_nr = treescore.sum_rootscore(tree4.treenode)

    lineage_score = treescore.lineage_score(tree.treenode)
    lineage_score_woutredundant = treescore.lineage_score_woutredundant(tree.treenode)

    taxdegree_score = treescore.lineage_score_tax_degree(tree.treenode,uniprot_df)


    species_set = set()
    #label the leaves with species and number
    for l in tree.treenode.get_leaves():
        if l.sp_num:
            l.name = l.sp_num
            species_set.add(l.sp_num)
    
    tree = ete3.Tree(tree.treenode)
    #calc number of losses and duplications
    events = tree.treenode.get_my_evol_events()
    dups = tree.search_nodes(evoltype="D")
    losses = tree.search_nodes(evoltype="L")

    #use species tree based algorithm to calculate loss and duplication events
    sptree = tree = ncbi.get_topology(species_set)

    #output the species tree
    sptree.write(outfile=snakemake.output[1], format=1)
    
    recon_tree, events = genetree.reconcile(sptree)
    dups_recon = recon_tree.search_nodes(evoltype="D")
    losses_recon = recon_tree.search_nodes(evoltype="L")

    #measure the distances of leaves to root
    distances = np.array([ node.get_distance(tree.treenode) for node in tree.treenode.get_leaves() ])
    distances_norm = distances / np.mean(distances)
    scores[t] = {'score': taxscore, 'stats': describe(lengths) , 'ultrametricity':  describe(distances), 
                 'ultrametricity_norm':  describe(distances_norm) , 'root_score': root_score  , 
                 'degree_score': degree_score1, 'lineage_score': lineage_score , 'lineage_score_woutredundant': lineage_score_woutredundant ,
                'degree_score1': degree_score1 , 'degree_score15': degree_score15 , 'degree_score2': degree_score2 , 'root_score_nr': root_score_nr
                , 'taxdegree_score': taxdegree_score }

print(scores)

with open(snakemake.output[0], 'w') as snakeout:
    snakeout.write( json.dumps( scores ) )



