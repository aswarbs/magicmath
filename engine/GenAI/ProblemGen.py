import random
import sympy as sp

class Problem():
    def __init__(self):
        pass

class CountdownProblem(Problem):
    def __init__(self, numbers, target, ops):
        self.numbers = numbers
        self.target = target
        self.ops = ops

class LinearEquationProblem(Problem):
    def __init__(self, equation, solution):
        self.equation = equation
        self.solution = solution

def generate_linear_equation_problem() -> Problem:
    # Function to generate a random equation
    def generate_equation():
        x = sp.symbols('x')
        equation_type = random.choice(['linear'])
        if equation_type == 'linear':
            a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(10, 50)
            eq = sp.Eq(a * x + b, c)
        return eq

    # Function to solve the equation
    def solve_equation(eq):
        x = sp.symbols('x')
        solution = sp.solve(eq, x)
        return solution

    eq = generate_equation()
    solution = solve_equation(eq)
    return LinearEquationProblem(eq, solution)

def generate_countdown_problem() -> Problem:
    # Step 1: Generate random target number between 100 and 999 (or any range you prefer)
    target_number = random.randint(100, 999)

    # Step 2: Generate 6 random numbers from two sets (4 large numbers, 2 small numbers)
    large_numbers = [random.randrange(0, 100) for _ in range(0, 50)]
    small_numbers = [random.randrange(0, 10) for _ in range(0, 50)]

    # Select 4 random large numbers and 2 random small numbers
    available_numbers = random.sample(large_numbers, 4) + random.sample(small_numbers, 2)

    return CountdownProblem(available_numbers, target_number, "+-/*")