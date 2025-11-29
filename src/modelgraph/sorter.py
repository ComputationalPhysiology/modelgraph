import re
import sys


def parse_ode_file(filename):
    """
    Reads an ODE file and returns a list of equations as strings.
    Handles multi-line expressions correctly.
    """
    equations = []
    with open(filename, "r") as f:
        buffer = ""
        parens = 0
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Count parentheses to detect multi-line expressions
            parens += stripped.count("(") - stripped.count(")")
            buffer += line
            if parens == 0:
                equations.append(buffer.strip())
                buffer = ""
    return equations


def get_dependencies(eq):
    """
    Returns a set of variables used on the RHS of an equation.
    """
    # Split on assignment
    if "=" not in eq:
        return set()
    lhs, rhs = eq.split("=", 1)
    # Match variable names (simplified)
    tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", rhs)
    # Exclude numbers and Python keywords
    numbers = re.compile(r"^\d+(\.\d+)?$")
    keywords = {"if", "else", "for", "while", "return", "and", "or", "not"}
    return set(t for t in tokens if not numbers.match(t) and t not in keywords)


def get_lhs(eq):
    """
    Returns the variable on the LHS of the equation.
    """
    return eq.split("=", 1)[0].strip()


def sort_equations(equations):
    """
    Topologically sorts equations based on dependencies.
    """
    lhs_map = {get_lhs(eq): eq for eq in equations}
    deps = {get_lhs(eq): get_dependencies(eq) for eq in equations}

    # Remove self dependencies and unknowns (external constants)
    for var in deps:
        deps[var] = set(d for d in deps[var] if d in lhs_map and d != var)

    sorted_eqs = []
    visited = set()
    temp_marks = set()

    def visit(node):
        if node in visited:
            return
        if node in temp_marks:
            raise ValueError(f"Cyclic dependency detected at {node}")
        temp_marks.add(node)
        for d in deps[node]:
            visit(d)
        temp_marks.remove(node)
        visited.add(node)
        sorted_eqs.append(lhs_map[node])

    for var in lhs_map:
        visit(var)

    return sorted_eqs


def main():
    if len(sys.argv) != 2:
        print("Usage: python sorter.py <ode_file>")
        return
    filename = sys.argv[1]
    equations = parse_ode_file(filename)
    sorted_eqs = sort_equations(equations)

    out_file = filename.replace(".ode", "_sorted.ode")
    with open(out_file, "w") as f:
        for eq in sorted_eqs:
            f.write(eq + "\n\n")
    print(f"Sorted ODE file written to {out_file}")


def sort_and_write(filename):
    equations = parse_ode_file(filename)
    sorted_eqs = sort_equations(equations)
    out_file = filename.replace(".ode", "_sorted.ode")

    with open(out_file, "w") as f:
        for eq in sorted_eqs:
            f.write(eq + "\n\n")
    return out_file


if __name__ == "__main__":
    main()
