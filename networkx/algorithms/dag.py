# -*- coding: utf-8 -*-
from fractions import gcd
import networkx as nx
from .traversal.breadth_first_search import bfs_tree
"""Algorithms for directed acyclic graphs (DAGs)."""
#    Copyright (C) 2006-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                            'Dan Schult (dschult@colgate.edu)',
                            'Ben Edwards (bedwards@cs.unm.edu)'])
__all__ = ['descendants',
           'ancestors',
           'topological_sort', 
           'topological_sort_recursive',
           'is_directed_acyclic_graph',
           'is_aperiodic']

def descendants(G, source, check_dag=False, reverse=False):
    """Return all nodes reachable from `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G
    check_dag : bool, optional
        Check whether G is a DAG before running the algorithm. If G is not a
        DAG, the results may not be meaningful. (default: False, as the check
        is expensive.)
    reverse : bool, optional
        Whether to invert the direction of the edges of the graph during the
        search, resulting in a search for ancestors instead. (default: False.)

    Returns
    -------
    descendants : set()
       The descendants of source in G
    """
    if check_dag and not is_directed_acyclic_graph(G):
        raise ValueError("ancestors() is only defined for DAGs")
    if not G.has_node(source):
        raise nx.NetworkXError("The node %s is not in the graph." % source)
    return set(bfs_tree(G, source, reverse=reverse).nodes()) - set([source])

def ancestors(G, source, check_dag=False):
    """Return all nodes having a path to `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G

    Returns
    -------
    ancestors : set()
       The ancestors of source in G
    """
    return descendants(G, source, check_dag=check_dag, reverse=True)

def is_directed_acyclic_graph(G):
    """Return True if the graph G is a directed acyclic graph (DAG) or 
    False if not.
    
    Parameters
    ----------
    G : NetworkX graph
      A graph

    Returns
    -------
    is_dag : bool
       True if G is a DAG, false otherwise
    """
    try:
        topological_sort(G)
        return True
    except nx.NetworkXUnfeasible:
        return False

def topological_sort(G,nbunch=None):
    """Return a list of nodes in topological sort order.

    A topological sort is a nonunique permutation of the nodes
    such that an edge from u to v implies that u appears before v in the
    topological sort order.

    Parameters
    ----------
    G : NetworkX digraph
       A directed graph

    nbunch : container of nodes (optional)
       Explore graph in specified order given in nbunch

    Raises
    ------
    NetworkXError
       Topological sort is defined for directed graphs only. If the
       graph G is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
       If G is not a directed acyclic graph (DAG) no topological sort
       exists and a NetworkXUnfeasible exception is raised.

    Notes
    -----
    This algorithm is based on a description and proof in
    The Algorithm Design Manual [1]_ .

    See also
    --------
    is_directed_acyclic_graph

    References
    ----------
    .. [1] Skiena, S. S. The Algorithm Design Manual  (Springer-Verlag, 1998). 
        http://www.amazon.com/exec/obidos/ASIN/0387948600/ref=ase_thealgorithmrepo/
    """
    if not G.is_directed():
        raise nx.NetworkXError(
                "Topological sort not defined on undirected graphs.")

    # nonrecursive version
    seen = set()
    order = [] 
    explored = set() 
                     
    if nbunch is None:
        nbunch = G.nodes_iter() 
    for v in nbunch:     # process all vertices in G
        if v in explored: 
            continue
        fringe = [v]   # nodes yet to look at
        while fringe:
            w = fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen.add(w)     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes = []
            for n in G[w]:
                if n not in explored:
                    if n in seen: #CYCLE !!
                        raise nx.NetworkXUnfeasible("Graph contains a cycle.")
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored.add(w)
                order.append(w)
                fringe.pop()    # done considering this node
    return list(reversed(order))

def topological_sort_recursive(G,nbunch=None):
    """Return a list of nodes in topological sort order.

    A topological sort is a nonunique permutation of the nodes such
    that an edge from u to v implies that u appears before v in the
    topological sort order.

    Parameters
    ----------
    G : NetworkX digraph

    nbunch : container of nodes (optional)
       Explore graph in specified order given in nbunch

    Raises
    ------
    NetworkXError
       Topological sort is defined for directed graphs only. If the
       graph G is undirected, a NetworkXError is raised.

    NetworkXUnfeasible
        If G is not a directed acyclic graph (DAG) no topological sort
        exists and a NetworkXUnfeasible exception is raised.

    Notes
    -----
    This is a recursive version of topological sort.

    See also
    --------
    topological_sort
    is_directed_acyclic_graph

    """
    if not G.is_directed():
        raise nx.NetworkXError(
            "Topological sort not defined on undirected graphs.")

    def _dfs(v):
        ancestors.add(v)

        for w in G[v]:
            if w in ancestors:
                raise nx.NetworkXUnfeasible("Graph contains a cycle.")

            if w not in explored:
                _dfs(w)

        ancestors.remove(v)
        explored.add(v)
        order.append(v)

    ancestors = set()
    explored = set()
    order = []

    if nbunch is None:
        nbunch = G.nodes_iter()

    for v in nbunch:
        if v not in explored:
            _dfs(v)
            
    return list(reversed(order))

def is_aperiodic(G):
    """Return True if G is aperiodic.

    A directed graph is aperiodic if there is no integer k > 1 that 
    divides the length of every cycle in the graph.

    Parameters
    ----------
    G : NetworkX DiGraph
      Graph

    Returns
    -------
    aperiodic : boolean
      True if the graph is aperiodic False otherwise

    Raises
    ------
    NetworkXError
      If G is not directed

    Notes
    -----
    This uses the method outlined in [1]_, which runs in O(m) time
    given m edges in G. Note that a graph is not aperiodic if it is
    acyclic as every integer trivial divides length 0 cycles.

    References
    ----------
    .. [1] Jarvis, J. P.; Shier, D. R. (1996),
       Graph-theoretic analysis of finite Markov chains,
       in Shier, D. R.; Wallenius, K. T., Applied Mathematical Modeling:
       A Multidisciplinary Approach, CRC Press.
    """
    if not G.is_directed():
        raise nx.NetworkXError("is_aperiodic not defined for undirected graphs")

    s = next(G.nodes_iter())
    levels = {s:0}
    this_level = [s]
    g = 0
    l = 1
    while this_level:
        next_level = []
        for u in this_level:
            for v in G[u]:
                if v in levels: # Non-Tree Edge
                    g = gcd(g, levels[u]-levels[v] + 1)
                else: # Tree Edge
                    next_level.append(v)
                    levels[v] = l
        this_level = next_level
        l += 1
    if len(levels)==len(G): #All nodes in tree
        return g==1
    else:
        return g==1 and nx.is_aperiodic(G.subgraph(set(G)-set(levels)))
