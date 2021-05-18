# https://github.com/marcmelis/dpll-sat/blob/master/solvers/original_dpll.py
from collections import defaultdict

def parse_dimacs(filename):
    formula = []
    n_props = None
    with open(filename, "r") as f:
        for line in f:
            if not len(line.strip()): continue
            if line[0] in ["c", "0", "%"]: continue
            elif line[0] == "p": n_props = int(line.strip().split()[2])
            else:
                clause = [int(p) for p in line.strip().split()[:-1]]
                formula.append(clause)
    return formula, n_props


def count_literals(formula):
    """
    Counts the times each literal appears in the formula
    """
    counts = defaultdict(int)
    for clause in formula:
        for literal in clause:
            counts[literal] += 1
    return counts

def _make_literal_true(formula, literal):
    """
    Modifies the formula according to a true valuation for literal
    """
    new_formula = []
    for clause in formula:
        if literal in clause: continue # We make the literal true so we remove clauses that contains it
        new_clause = clause[:]
        if -1*literal in clause:
            new_clause.remove(-1 * literal)
            if len(new_clause) == 0: return -1 # No literals left in clause so the formula is unsatisfiable
            new_formula.append(new_clause)
        else:
            new_formula.append(new_clause)
    return new_formula


def make_literals_true(formula, literals):
    """
    Wrapper of _make_literal_true to support list of literals
    """
    if not isinstance(literals, list):
        return _make_literal_true(formula, literals)
    for literal in literals:
        formula = _make_literal_true(formula, literal)
    return formula


def ple(formula):
    """
    Performs Pure Literal Elimination step.
    Returns updated formula and new assigned literals
    """
    literal_counts = count_literals(formula)
    pure_literals = []
    for literal in literal_counts.keys():
        if -1*literal not in literal_counts:
            pure_literals.append(literal)

    formula = make_literals_true(formula, pure_literals)
    return formula, pure_literals

def get_unit_clause(formula):
    """
    Returns first clause that contains only one literal if any otherwise returns None
    """
    for clause in formula: 
        if len(clause) == 1: return clause
    return None


def up(formula):
    """
    Performs Unit Propagation.
    Returns updated formula and new assigned literals.
    """
    valuation = []
    unit_clause = get_unit_clause(formula)
    while unit_clause is not None:
        unique_literal = unit_clause[0]
        formula = make_literals_true(formula, unique_literal)
        valuation.append(unique_literal)
        if formula == -1:
            return -1, []
        if not formula:
            return formula, valuation
        unit_clause = get_unit_clause(formula)
    return formula, valuation

def select_next_literal(formula):
    """
    Selects next literal to be assigned by finding the first unassigned literal.
    """
    for clause in formula:
        return clause[0]

def _dpll(formula, valuation):
    formula, pure_valuation = ple(formula)
    formula, unit_valuation = up(formula)
    valuation = valuation + pure_valuation + unit_valuation
    if formula == - 1:
        return []
    if not formula:
        return valuation
    literal = select_next_literal(formula)
    for sign in (1, -1):
        solution = _dpll(make_literals_true(formula, sign*literal), valuation + [sign*literal])
        if solution:
            return solution
    return []

def dpll(filename):
    formula, n_props = parse_dimacs(filename)
    solution = _dpll(formula, [])

    if not solution:
        return None
    solution = [i for i in range(1, n_props+1) if i not in solution and -i not in solution] + solution
    solution.sort(key=lambda x: abs(x))
    return solution

if __name__ == "__main__":
    import time
    t = time.time()
    res = dpll("satisfiable.cnf")
    t = time.time() - t
    print(f"Satisfiable problem solved in {t:.4f}s,  Solution:", res)

    t = time.time()
    res = dpll("unsatisfiable.cnf")
    t = time.time() - t
    print(f"Unsatisfiable problem solved in {t:.4f}s,  Solution:", res)
