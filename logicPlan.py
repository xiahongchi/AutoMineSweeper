# logicPlan.py
# ------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In logicPlan.py, you will implement logic planning methods which are called by
Pacman agents (in logicAgents.py).
"""

from typing import Dict, List, Tuple, Callable, Generator, Any
import util
import sys
import logic


from logic import conjoin, disjoin
from logic import PropSymbolExpr, Expr, to_cnf, pycoSAT, parseExpr, pl_true

import itertools
import copy

pacman_str = 'P'
food_str = 'FOOD'
wall_str = 'WALL'
pacman_wall_str = pacman_str + wall_str
ghost_pos_str = 'G'
ghost_east_str = 'GE'
pacman_alive_str = 'PA'
DIRECTIONS = ['North', 'South', 'East', 'West']
blocked_str_map = dict([(direction, (direction + "_blocked").upper()) for direction in DIRECTIONS])
geq_num_adj_wall_str_map = dict([(num, "GEQ_{}_adj_walls".format(num)) for num in range(1, 4)])
DIR_TO_DXDY_MAP = {'North':(0, 1), 'South':(0, -1), 'East':(1, 0), 'West':(-1, 0)}


#______________________________________________________________________________
# QUESTION 1

def sentence1() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    A or B
    (not A) if and only if ((not B) or C)
    (not A) or (not B) or C
    """
    "*** BEGIN YOUR CODE HERE ***"
    A = Expr('A')
    B = Expr('B')
    C = Expr('C')
    c1 = A | B
    c2 = (~A) % ((~B) | C)
    c3 = disjoin([~A , ~B , C]) 
    return conjoin([c1,c2,c3])
    "*** END YOUR CODE HERE ***"


def sentence2() -> Expr:
    """Returns a Expr instance that encodes that the following expressions are all true.
    
    C if and only if (B or D)
    A implies ((not B) and (not D))
    (not (B and (not C))) implies A
    (not D) implies C
    """
    "*** BEGIN YOUR CODE HERE ***"
    A = Expr('A')
    B = Expr('B')
    C = Expr('C')
    D = Expr('D')
    c1 = C % (B | D)
    c2 = A >> ((~B) & (~D))
    c3 = (~(B & (~C))) >> A 
    c4 = (~D) >> C
    return conjoin([c1,c2,c3,c4])
    "*** END YOUR CODE HERE ***"


def sentence3() -> Expr:
    """Using the symbols PacmanAlive_1 PacmanAlive_0, PacmanBorn_0, and PacmanKilled_0,
    created using the PropSymbolExpr constructor, return a PropSymbolExpr
    instance that encodes the following English sentences (in this order):

    Pacman is alive at time 1 if and only if Pacman was alive at time 0 and it was
    not killed at time 0 or it was not alive at time 0 and it was born at time 0.

    Pacman cannot both be alive at time 0 and be born at time 0.

    Pacman is born at time 0.
    (Project update: for this question only, [0] and _t are both acceptable.)
    """
    "*** BEGIN YOUR CODE HERE ***"
    PacmanAlive_0 = PropSymbolExpr('PacmanAlive',time=0)
    PacmanAlive_1 = PropSymbolExpr('PacmanAlive',time=1)
    PacmanBorn_0 = PropSymbolExpr('PacmanBorn',time=0)
    PacmanKilled_0 = PropSymbolExpr('PacmanKilled',time=0)

    c1 = PacmanAlive_1 % ((PacmanAlive_0 & (~PacmanKilled_0)) | ((~PacmanAlive_0) & PacmanBorn_0))
    c2 = ~(PacmanAlive_0 & PacmanBorn_0)
    c3 = PacmanBorn_0
    return conjoin([c1,c2,c3])
    "*** END YOUR CODE HERE ***"

def findModel(sentence: Expr) -> Dict[Expr, bool]:
    """Given a propositional logic sentence (i.e. a Expr instance), returns a satisfying
    model if one exists. Otherwise, returns False.
    """
    cnf_sentence = to_cnf(sentence)
    return pycoSAT(cnf_sentence)

def findModelCheck() -> Dict[Any, bool]:
    """Returns the result of findModel(Expr('a')) if lower cased expressions were allowed.
    You should not use findModel or Expr in this method.
    This can be solved with a one-line return statement.
    """
    class dummyClass:
        """dummy('A') has representation A, unlike a string 'A' that has repr 'A'.
        Of note: Expr('Name') has representation Name, not 'Name'.
        """
        def __init__(self, variable_name: str = 'A'):
            self.variable_name = variable_name
        
        def __repr__(self):
            return self.variable_name
    "*** BEGIN YOUR CODE HERE ***"
    return {dummyClass('a'): True}
    "*** END YOUR CODE HERE ***"

def entails(premise: Expr, conclusion: Expr) -> bool:
    """Returns True if the premise entails the conclusion and False otherwise.
    """
    "*** BEGIN YOUR CODE HERE ***"
    c = premise & (~conclusion)
    return findModel(c) == False
    "*** END YOUR CODE HERE ***"

def plTrueInverse(assignments: Dict[Expr, bool], inverse_statement: Expr) -> bool:
    """Returns True if the (not inverse_statement) is True given assignments and False otherwise.
    pl_true may be useful here; see logic.py for its description.
    """
    "*** BEGIN YOUR CODE HERE ***"
    return pl_true((~inverse_statement), assignments)
    "*** END YOUR CODE HERE ***"

#______________________________________________________________________________
# QUESTION 2

def atLeastOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals (i.e. in the form A or ~A), return a single 
    Expr instance in CNF (conjunctive normal form) that represents the logic 
    that at least one of the literals is true.
    >>> A = PropSymbolExpr('A');
    >>> B = PropSymbolExpr('B');
    >>> symbols = [A, B]
    >>> atleast1 = atLeastOne(symbols)
    >>> model1 = {A:False, B:False}
    >>> print(pl_true(atleast1,model1))
    False
    >>> model2 = {A:False, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    >>> model3 = {A:True, B:True}
    >>> print(pl_true(atleast1,model2))
    True
    """
    "*** BEGIN YOUR CODE HERE ***"
    return disjoin(literals)
    "*** END YOUR CODE HERE ***"


def atMostOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form) that represents the logic that at most one of 
    the expressions in the list is true.
    itertools.combinations may be useful here.
    """
    "*** BEGIN YOUR CODE HERE ***"
    rs = [(~e1 | ~e2) for e1, e2 in itertools.combinations(literals, 2)]
    return conjoin(rs)
   

def exactlyOne(literals: List[Expr]) -> Expr:
    """
    Given a list of Expr literals, return a single Expr instance in 
    CNF (conjunctive normal form)that represents the logic that exactly one of 
    the expressions in the list is true.
    """
    "*** BEGIN YOUR CODE HERE ***"
    return conjoin([atLeastOne(literals) , atMostOne(literals)])

#______________________________________________________________________________
# FOR MINESWEEPER

### for mines
def atMostTwo(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3) for e1, e2, e3 in itertools.combinations(literals, 3)]
    return conjoin(rs)

def atMostThree(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3|~e4) for e1, e2, e3, e4 in itertools.combinations(literals, 4)]
    return conjoin(rs)
    
def atMostFour(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3|~e4|~e5) for e1, e2, e3, e4, e5 in itertools.combinations(literals, 5)]
    return conjoin(rs)

def atMostFive(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3|~e4|~e5|~e6) for e1, e2, e3, e4, e5, e6 in itertools.combinations(literals, 6)]
    return conjoin(rs)
    
def atMostSix(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3|~e4|~e5|~e6|~e7) for e1, e2, e3, e4, e5, e6, e7 in itertools.combinations(literals, 7)]
    return conjoin(rs)
    
def atMostSeven(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    rs = [(~e1|~e2|~e3|~e4|~e5|~e6|~e7|~e8) for e1, e2, e3, e4, e5, e6, e7, e8 in itertools.combinations(literals, 8)]
    return conjoin(rs)

def exactlyEight(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    return conjoin(literals)

def exactlySeven(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostOne(negalist), atMostSeven(literals)])

def exactlySix(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostTwo(negalist), atMostSix(literals)])

def exactlyFive(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostThree(negalist), atMostFive(literals)])

def exactlyFour(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostFour(negalist), atMostFour(literals)])

def exactlyThree(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostFive(negalist), atMostThree(literals)])

def exactlyTwo(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin([atMostSix(negalist), atMostTwo(literals)])

def exactlyZero(literals: List[Expr]) -> Expr:
    assert(len(literals) == 8)
    negalist = [~literal for literal in literals]
    return conjoin(negalist)

### for walls 

mine_str = "MINE"
wall_str = "WALL"

def wallAxioms(x, y):
    sent_axioms = []
    for i in range(x+2):
        sent_axioms.append(~PropSymbolExpr(mine_str, i, 0))
        sent_axioms.append(~PropSymbolExpr(mine_str, i, y+1))
    for j in range(y+2):
        sent_axioms.append(~PropSymbolExpr(mine_str, 0, j))
        sent_axioms.append(~PropSymbolExpr(mine_str, x+1, j))

    return conjoin(sent_axioms)

### for generating literals
adjacent_pairs = [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]

def adjacentAxioms(x, y, num):
    assert(num >= 0 and num <= 8)
    literals = []
    for dx, dy in adjacent_pairs:
        corr_x, corr_y = x+dx, y+dy
        literals.append(PropSymbolExpr(mine_str, corr_x, corr_y))

    if num == 0:
        return exactlyZero(literals)
    elif num == 1:
        return exactlyOne(literals)
    elif num == 2:
        return exactlyTwo(literals)
    elif num == 3:
        return exactlyThree(literals)
    elif num == 4:
        return exactlyFour(literals)
    elif num == 5:
        return exactlyFive(literals)
    elif num == 6:
        return exactlySix(literals)
    elif num == 7:
        return exactlySeven(literals)
    elif num == 8:
        return exactlyEight(literals)
