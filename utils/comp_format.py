import os


class Solution:
    def __init__(self):
        # the tour of the thief
        self.pi = []
        # the packing plan
        self.z = []
        # the time the thief needed for traveling
        self.time = -1.0
        # the profit the thief made on that tour
        self.profit = -1.0
        # objective value if you want to solve the single-objective problem using R
        self.singleObjective = -1.0
        # the objective values of the function
        self.objectives = []

    def get_relation(self, other):
        """
        This is used for non-dominated sorting and returns the dominance relation
        :param other: solution to compare with
        :return: returns 1 if dominates, -1 if dominated and 0 if indifferent
        """
        val = 0
        for i in range(len(self.objectives)):
            if self.objectives[i] < other.objectives[i]:
                if val == -1:
                    return 0
                val = 1
            elif self.objectives[i] > other.objectives[i]:
                if val == 1:
                    return 0
                val = -1
        return val

    def equals_in_design_space(self, other):
        """
        :param other: solution to compare with
        :return: True if tour and packing plan is equal
        """
        return self.pi == other.pi and self.z == other.z


class NonDominatedSet:
    def __init__(self):
        # entries of the non-dominated set
        self.entries = []

    def add(self, s):
        """
        Add a solution to the non-dominated set
        :param s: The solution to be added.
        :return: true if the solution was indeed added. Otherwise false.
        """
        is_added = True

        for other in self.entries[:]:
            rel = s.get_relation(other)

            # if dominated by or equal in design space
            if rel == -1 or (rel == 0 and s.equals_in_design_space(other)):
                is_added = False
                break
            elif rel == 1:
                self.entries.remove(other)

        if is_added:
            self.entries.append(s)

        return is_added


class CompStore:
    """Store the solutions in the format for the competition"""

    def __init__(self, team, problem):
        self.team = team
        self.problem = problem
    # write the solutions to a file .x

    def write_solution(self, solutions):
        folder_path = os.path.join(os.getcwd(), '../Result')
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'{self.team}_{self.problem}.x')
        with open(file_path, 'w') as f:
            for solution in solutions:
                f.write(' '.join(map(str, solution.pi)) + '\n')
                f.write(' '.join(map(str, solution.z)) + '\n\n')
    # write the objectives to a file .f

    def write_objectives(self, solutions):
        folder_path = os.path.join(os.getcwd(), '../Result')
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f'{self.team}_{self.problem}.f')
        with open(file_path, 'w') as f:
            for solution in solutions:
                f.write(f'{solution.time} {solution.profit}\n')
