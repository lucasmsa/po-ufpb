from __future__ import print_function
from ortools.linear_solver import pywraplp

class MaximumFlow:
    def __init__(self, input_file):
        self.input_file = input_file
        self.solver = pywraplp.Solver.CreateSolver('GLOP')
        self.origin_nodes = []
        self.destiny_nodes = []
        self.capacities = []
        self.constraints = []
        self.arcs = {}
    
    def read_file(self):
        with open(self.input_file, 'r') as f:
            problem_data = f.read().splitlines()
            self.vertices_arcs = {}
            
            self.vertices, self.num_arcs, self.source, self.sink = problem_data[0:4]
            self.arcs_data = problem_data[4:]
            
            for arc in self.arcs_data:
                origin_node, destiny_node, capacity = arc.split()
                arc_name = f'x{origin_node}{destiny_node}'
                
                try:
                    self.vertices_arcs[origin_node]["origin_arcs"].append(arc_name)
                except:
                    self.vertices_arcs[origin_node] = {'origin_arcs': [arc_name], 'destiny_arcs': []}

                try:
                    self.vertices_arcs[destiny_node]["destiny_arcs"].append(arc_name)

                except:
                    self.vertices_arcs[destiny_node] = {'origin_arcs': [], 'destiny_arcs': [arc_name]}
                
                self.arcs[arc_name] = self.solver.NumVar(0, float(capacity), arc_name)
            
            self.arcs[f'x{self.source}{self.sink}'] = self.solver.NumVar(0, self.solver.infinity(), f'x{self.source}{self.sink}')
                
    def set_constraints(self):
        for vertice, arcs in self.vertices_arcs.items():
            conservation_constraint = self.solver.Constraint(0, 0)
            if vertice != self.source and vertice != self.sink:

                for origin_arc in arcs['origin_arcs']:
                    conservation_constraint.SetCoefficient(self.arcs[origin_arc], 1)
                for destiny_arc in arcs['destiny_arcs']:
                    conservation_constraint.SetCoefficient(self.arcs[destiny_arc], -1)
             
            elif vertice == self.sink:
                
                for arc in arcs['destiny_arcs']:
                    conservation_constraint.SetCoefficient(self.arcs[arc], -1)
                
                conservation_constraint.SetCoefficient(self.arcs[f'x{self.source}{self.sink}'], 1)
        
    def set_objective_function(self):
        objective = self.solver.Objective()
            
        objective.SetCoefficient(self.arcs[f'x{self.source}{self.sink}'], -1)
            
        objective.SetMinimization()
    
    def solve(self):
        self.solver.Solve()
        for arc in self.arcs:
            print(self.arcs[arc].lb(), self.arcs[arc].ub(), self.arcs[arc].solution_value())

        print(self.arcs[f'x{self.source}{self.sink}'].solution_value())
        
        
maximum_flow = MaximumFlow(input_file='input/instancias/instance1.txt')
maximum_flow.read_file()
maximum_flow.set_constraints()
maximum_flow.set_objective_function()
maximum_flow.solve()