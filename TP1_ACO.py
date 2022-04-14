import random
import time
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfile

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)


# https://pypi.org/project/ACO-Pants/  for compare results with

class AntColony(object):
    def __init__(self, distances, n_ants, n_best, decay, alpha, beta, Q, stop_condition):
        self.distances = distances
        self.all_sommets = range(len(distances))
        self.n_ants = n_ants
        self.n_best = n_best
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.Q = Q
        self.stop_condition = stop_condition
        self.pheromone = np.ones(self.distances.shape)  # ?khởi  tạo  =?
        np.fill_diagonal(self.pheromone, 0)

    def roulette_wheel(self, all_sommets, probabilities):
        r = random.random()
        for i in range(len(probabilities)):
            if r <= probabilities[i]:
                move = all_sommets[i]
                break
        return move

    def pick_move(self, pheromone, distance, visited):
        pheromone1 = np.copy(pheromone)
        pheromone1[list(visited)] = 0
        row = pheromone1 ** self.alpha * ((1.0 / distance) ** self.beta)
        norm_row = row / row.sum()
        probabilities = [sum(norm_row[:i + 1]) for i in range(len(norm_row))]
        move = self.roulette_wheel(self.all_sommets, probabilities)
        return move

    def generate_path(self, start, goal):
        path = []
        visited = set()
        visited.add(start)
        prev = start
        move = start
        while (move != goal):
            move = self.pick_move(self.pheromone[prev], self.distances[prev], visited)
            path.append((prev, move))  # path =[start , move]
            prev = move  # set prev=move
            visited.add(move)  # set visited = start, move
        return path

    def generate_all_paths(self, start, goal):
        all_paths = []
        for i in range(self.n_ants):
            path = self.generate_path(start, goal)
            all_paths.append((path, self.gen_path_dist(path)))
        return all_paths

    def gen_path_dist(self, path):
        total_dist = 0
        for sommet in path:
            total_dist += self.distances[sommet]
        return total_dist

    def update_pheromone(self, all_paths, n_best):
        self.pheromone = self.pheromone * (1 - self.decay)
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        for path, dist in sorted_paths[:n_best]:
            for move in path:
                self.pheromone[move] += self.Q / dist

    def run(self, start, goal):
        final_shortest_path = ("placeholder", np.inf)
        global G, simulator_canvas
        i = 0
        while True:
            all_paths = self.generate_all_paths(start, goal)
            print("iteration number " + str(i))
            print(str(all_paths))
            # update simulator
            if on_simulator.get() == 1:
                simulator_canvas.get_tk_widget().pack_forget()
                fig_s = plt.Figure(figsize=(4, 3))
                a1 = fig_s.add_subplot(111)
                pos = nx.circular_layout(G)
                for path in all_paths:
                    for edge in path[0]:
                        G[edge[0]][edge[1]]['color'] += (1/ self.n_ants)
                        G[edge[0]][edge[1]]['w'] += (0.05 / self.n_ants)
                colors = nx.get_edge_attributes(G, 'color').values()
                widthx = list(nx.get_edge_attributes(G, 'w').values())
                nx.draw_networkx(G, pos=pos, ax=a1, edge_color=colors, edge_cmap=plt.cm.Blues, width=widthx,
                                 font_color='white',
                                 node_color=node_colors)
                simulator_canvas = FigureCanvasTkAgg(fig_s, canvasframe)
                simulator_canvas.get_tk_widget().pack(pady=10)
                simulator_canvas.draw()
                root.update()
            # ----end update
            self.update_pheromone(all_paths, self.n_best)
            shortest_path = min(all_paths, key=lambda x: x[1])
            print("shortest_path: ")
            print(str(shortest_path))
            if shortest_path[1] < final_shortest_path[1]:
                final_shortest_path = shortest_path
            # check stop_condition
            count_path = sum(path[0] == final_shortest_path[0] for path in all_paths)
            if self.n_ants * self.stop_condition <= count_path:
                result.insert(END, "Success: " + str(float(count_path / self.n_ants) * 100) + "%\n")
                if on_simulator.get() != 1:
                    simulator_canvas.get_tk_widget().pack_forget()
                    fig_s = plt.Figure(figsize=(4, 3))
                    a1 = fig_s.add_subplot(111)
                    pos = nx.circular_layout(G)
                    for edge in final_shortest_path[0]:
                        G[edge[0]][edge[1]]['color'] += 5
                        G[edge[0]][edge[1]]['w'] += 2
                    colors = nx.get_edge_attributes(G, 'color').values()
                    widthx = list(nx.get_edge_attributes(G, 'w').values())
                    nx.draw_networkx(G, pos=pos, ax=a1, edge_color=colors, edge_cmap=plt.cm.Blues, width=widthx,
                                     font_color='white',
                                     node_color=node_colors)
                    simulator_canvas = FigureCanvasTkAgg(fig_s, canvasframe)
                    simulator_canvas.get_tk_widget().pack(pady=10)
                    simulator_canvas.draw()
                root.update()
                break
            i = i + 1
            print("------------------------")
        return final_shortest_path


def disable_config():
    # Disable config side
    startbutton.config(state='disabled')
    matrix_button.config(state='disabled')
    e_nants["state"] = "disabled"
    e_nbest["state"] = "disabled"
    e_decay["state"] = "disabled"
    e_alpha["state"] = "disabled"
    e_beta["state"] = "disabled"
    e_snode["state"] = "disabled"
    e_gnode["state"] = "disabled"
    e_Q["state"] = "disabled"
    e_scond["state"] = "disabled"
    root.update()


def enable_config():
    # Enable config side
    startbutton.config(state='active')
    matrix_button.config(state='active')
    e_nants["state"] = "normal"
    e_nbest["state"] = "normal"
    e_decay["state"] = "normal"
    e_alpha["state"] = "normal"
    e_beta["state"] = "normal"
    e_snode["state"] = "normal"
    e_gnode["state"] = "normal"
    e_Q["state"] = "normal"
    e_scond["state"] = "normal"
    root.update()


def gen_simulator_canvas():
    global G, simulator_canvas
    simulator_canvas.get_tk_widget().pack_forget()
    # simulator canvas
    fig_s = plt.Figure(figsize=(4, 3))
    a1 = fig_s.add_subplot(111)
    pos = nx.circular_layout(G)
    for e in G.edges:
        G[e[0]][e[1]]['color'] = 0
        G[e[0]][e[1]]['w'] = 1.0
    colors = nx.get_edge_attributes(G, 'color').values()
    widthx = list(nx.get_edge_attributes(G, 'w').values())
    start_n = int(e_snode.get())
    goal_n = int(e_gnode.get())
    global node_colors
    node_colors = []
    for node in G:
        if node == start_n:
            node_colors.append('green')
        elif node == goal_n:
            node_colors.append('orange')
        else:
            node_colors.append('blue')
    nx.draw_networkx(G, pos=pos, ax=a1, edge_color=colors, edge_cmap=plt.cm.Blues, width=widthx, font_color='white',
                     node_color=node_colors)
    simulator_canvas = FigureCanvasTkAgg(fig_s, canvasframe)
    simulator_canvas.get_tk_widget().pack(pady=10)
    simulator_canvas.draw()


def warning_popup():
    if on_simulator.get() == 1:
        messagebox.showerror("Warning", "Turn on simulator will slow down program!")


def start():
    result.delete('1.0', END)
    gen_simulator_canvas()
    root.update()
    if 'matrix_data' not in globals():
        messagebox.showerror("Error", "You must load matrix first!")
    else:
        distances = np.array(matrix_data)
        n_ants = int(e_nants.get())
        n_best = int(e_nbest.get())
        decay = float(e_decay.get())
        alpha = float(e_alpha.get())
        beta = float(e_beta.get())
        start_n = int(e_snode.get())
        goal_n = int(e_gnode.get())
        Q = int(e_Q.get())
        stop_condition = float(e_scond.get())
        disable_config()
        ant_colony = AntColony(distances, n_ants, n_best, decay, alpha, beta, Q, stop_condition)
        t_start = time.time()
        shortest_path = ant_colony.run(start_n, goal_n)
        result.insert(END, "Shortest path: {}\n".format(shortest_path))
        result.insert(END, "Run time: " + str(time.time() - t_start) + "\n")
        root.update()
        enable_config()


def open_file():
    file = askopenfile(mode='r', filetypes=[('Data files', '*.txt')])
    if file is not None:
        global matrix_data
        matrix_data = [[int(num) if int(num) != -1 else np.inf for num in line.split(' ')] for line in file]
        print(matrix_data)

        global G, in_canvas
        in_canvas.get_tk_widget().pack_forget()
        # Input graph canvas
        fig_n = plt.Figure(figsize=(4, 3))
        a = fig_n.add_subplot(111)
        plt.axis('off')
        G = nx.from_numpy_array(np.array(matrix_data))
        G.edges(data=True)
        pos = nx.circular_layout(G)
        nx.draw_networkx(G, pos=pos, ax=a, with_labels=True, font_color='white')
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=pos, ax=a, edge_labels=labels, font_size=10)
        in_canvas = FigureCanvasTkAgg(fig_n, canvasframe)
        in_canvas.get_tk_widget().pack(pady=10)
        in_canvas.draw()
        gen_simulator_canvas()


# -----------------------------------UI-----------------------------------
root = Tk()
root.geometry("1200x700")
root.title("Algorithm ACO")
frame = Frame(root, width=1200, height=700)
frame.pack(padx=10)

# Config --Start
leftframe = Frame(frame, width=300, height=400)
leftframe.grid_propagate(False)
leftframe.grid(row=0, column=0, padx=10)

l_nants = Label(leftframe, text="Number of ants: ").grid(row=0, column=0, sticky="W", pady=4)
e_nants = Entry(leftframe, width=10)
e_nants.insert(0, '100')
e_nants.grid(row=0, column=1)

l_nbest = Label(leftframe, text="№ of ants used to update pheromone: ").grid(row=1, column=0, sticky="W", pady=4)
e_nbest = Entry(leftframe, width=10)
e_nbest.insert(0, '10')
e_nbest.grid(row=1, column=1)

l_decay = Label(leftframe, text="Decay rate: ").grid(row=2, column=0, sticky="W", pady=4)
e_decay = Entry(leftframe, width=10)
e_decay.insert(0, '0.2')
e_decay.grid(row=2, column=1)

l_alpha = Label(leftframe, text="Alpha (α): ").grid(row=3, column=0, sticky="W", pady=4)
e_alpha = Entry(leftframe, width=10)
e_alpha.insert(0, '0.6')
e_alpha.grid(row=3, column=1)

l_beta = Label(leftframe, text="Beta (β): ").grid(row=4, column=0, sticky="W", pady=4)
e_beta = Entry(leftframe, width=10)
e_beta.insert(0, '0.4')
e_beta.grid(row=4, column=1)

l_snode = Label(leftframe, text="Start node: ").grid(row=5, column=0, sticky="W", pady=4)
e_snode = Entry(leftframe, width=10)
e_snode.insert(0, '4')
e_snode.grid(row=5, column=1)

l_gnode = Label(leftframe, text="Goal node: ").grid(row=6, column=0, sticky="W", pady=4)
e_gnode = Entry(leftframe, width=10)
e_gnode.insert(0, '1')
e_gnode.grid(row=6, column=1)

l_Q = Label(leftframe, text="Decalage number: ").grid(row=7, column=0, sticky="W", pady=4)
e_Q = Entry(leftframe, width=10)
e_Q.insert(0, '100')
e_Q.grid(row=7, column=1)

l_scond = Label(leftframe, text="Stop condition: ").grid(row=8, column=0, sticky="W", pady=4)
e_scond = Entry(leftframe, width=10)
e_scond.insert(0, '0.95')
e_scond.grid(row=8, column=1)

on_simulator = IntVar()
simulator = Checkbutton(leftframe, text='Turn on simulator', variable=on_simulator, onvalue=1, offvalue=0,command=warning_popup).grid(row=9,
                                                                                                                column=0,
                                                                                                                sticky="W",
                                                                                                                pady=4)

padding_block1 = Label(leftframe, text="").grid(row=10, columnspan=2, sticky="W")
matrix_button = Button(leftframe, text="Load matrix from file", command=open_file, width=40)
matrix_button.grid(row=10, columnspan=2)

padding_block2 = Label(leftframe, text="").grid(row=11, columnspan=2, sticky="W")
startbutton = Button(leftframe, text="Start", command=start, width=40)
startbutton.grid(row=12, columnspan=2)
# Config --End

# Input graph and Algorithm simulator
canvasframe = Frame(frame, width=800, height=700)
canvasframe.grid_propagate(False)
canvasframe.grid(row=0, column=1, padx=30)
fig = plt.Figure(figsize=(4, 3))
in_canvas = FigureCanvasTkAgg(fig, canvasframe)
in_canvas.get_tk_widget().pack(pady=10)
in_canvas.draw()
simulator_canvas = FigureCanvasTkAgg(fig, canvasframe)
simulator_canvas.get_tk_widget().pack(pady=10)
simulator_canvas.draw()

# Result information --Start
rs_frame = Frame(frame, width=250, height=700)
rs_frame.grid_propagate(False)
rs_frame.grid(row=0, column=2, padx=10)
rs_label = Label(rs_frame, text="Result").pack()
result = Text(rs_frame, width=40, wrap="word")
result.pack()
scrollb_y = Scrollbar()
scrollb_y.place(in_=result, relx=1.0, relheight=1.0, bordermode="outside")
scrollb_y.configure(command=result.yview)
# Result information --End

# other params
root.mainloop()
# ------------------------------------------------------------------------
