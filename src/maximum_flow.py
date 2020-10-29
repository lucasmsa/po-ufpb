from os import name
from ortools.linear_solver import pywraplp
import fpdf
import sys
import networkx as nx
import matplotlib.pyplot as plt

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
        self.arcs_with_flow = [['Origin Arc', 'Destiny Arc', 'Flow']]
        for index, arc in enumerate(self.arcs):
            
            origin_node = str(self.arcs[arc])[1]
            destiny_node = str(self.arcs[arc])[2]
            flow = str(self.arcs[arc].solution_value())
            
            if index < len(self.arcs) - 1:
                self.arcs_with_flow.append([origin_node, destiny_node, flow])

        self.opt_solution = self.arcs[f'x{self.source}{self.sink}'].solution_value()
    
    def generate_pdf(self):
        pdf = fpdf.FPDF(format='letter')

        pdf.add_page()
        pdf.set_font("Arial", 'B', size=22)
        pdf.set_text_color(15, 7, 28)
        instance = sys.argv[1][:-1]
        instance_number = sys.argv[1][-1]
        
        pdf.cell(200, 7.5, f'Solution for {instance} {instance_number}', align='C')  
        
        
        pdf.set_font("Arial", size=10)
        
        th = pdf.font_size
        pdf.ln(4*th)
        pdf.ln(0.5)
        
        for arc in self.arcs_with_flow:
            for data in arc:
                pdf.cell(65, 2*th, str(data), border=1, align='C')
        
            pdf.ln(2*th)
        
        pdf.set_font("Arial", size=14)
        pdf.set_text_color(44, 88, 123)
        pdf.cell(200, 30, f'Optimal Solution - {self.opt_solution}', align='C')  

        self.generate_graph()
        pdf.set_font("Arial", 'I', size=12)
        pdf.set_text_color(15, 7, 28)
        pdf.cell(-200, 58, f'Resulting graph on the next page...', align='C')  
        pdf.add_page()
        pdf.image(name='output/flow_graph.png', x=10, y=0, w=192, h=144, link='https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be')
        pdf.output('output/maximum_flow_results.pdf')
        
    def generate_graph(self):
        DG = nx.DiGraph()
        f = plt.figure()
        edge_labels = {}
        
        for arc in self.arcs_with_flow[1:]:
            origin_node, destiny_node, flow = int(arc[0]), int(arc[1]), float(arc[2])
            DG.add_edge(origin_node, destiny_node, label=str(flow))
            edge_labels[(origin_node, destiny_node)] = flow
        
        pos = nx.spring_layout(DG)
        nx.draw_networkx(DG, pos=pos)
        nx.draw_networkx_edge_labels(DG, pos=pos, edge_labels=edge_labels)
        f.savefig('output/flow_graph.png')
        
         
maximum_flow = MaximumFlow(input_file=f'input/instancias/{sys.argv[1]}.txt')
maximum_flow.read_file()
maximum_flow.set_constraints()
maximum_flow.set_objective_function()
maximum_flow.solve()
maximum_flow.generate_pdf()