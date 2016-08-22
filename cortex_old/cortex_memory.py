import numpy as np
# import time
# import random
import timeit
import matplotlib.pylab as plt
# sys.setrecursionlimit(100000)


class Cell():
    def __init__(self, index = None, state = 0):
        self.index = ()
        self.state = 0.0
        self.state2 = 0.0
        self.f = 0
        self.u = 10.0  #voltage
        self.tau_u = 20.0 # ms
        self.prp = 10.0
        self.tau_prp = 2000.0 # ms
        self.tau_tag = 100.0 #ms
        self.A = 10.0  # target level of activation. Can be changed by neuromodulation
        self.saturation = 0.0
        self.stdp = 0


        self.syn_out = []
        self.syn_in = []
        self.syn_active = []


    def __repr__(self):
        return str(self.index)


class Synapse():
    def __init__(self, pre, post, strength = 0.0, delay = 1):
        self.pre = pre   # neuron's number that sends an action potention 
        self.post = post # neuron's number that receives an action potention 
        self.str = strength
        self.tag = 0.0
        self.is_active = 0


class Cortex():
    def __init__(self, dimension=()):
            self.dim = dimension
            self.t = 0
            self.cell_states = np.zeros(self.dim + (4,), dtype=np.ubyte)
            self.simple_states = np.zeros(self.dim, dtype=np.ubyte)
            self.create_cortex()
            print 'Cortex creted'
            self.W = np.zeros(625)
            self.raster_data = np.zeros((625, 5000))

    def create_cortex(self):
        self.cortex = np.empty(self.dim, dtype=object)
        self.cortex.flat = [Cell() for _ in self.cortex.flat]
        self.cell = Cell()

        for (z, x, y), cell in np.ndenumerate(self.cortex):
            cell.index = y
            self.add_syn_out(cell, [Synapse(cell, self.cell)])
            for synapse in cell.syn_out:
                self.add_syn_in(synapse.post, synapse)  # set input synapses to the cell
                synapse.str = np.random.randint(10)

    def live(self):
        self.t += 1
        if self.t % 100 == 0:
        #     print self.t
            print self.cell.f
            self.cell.f = 0
        self.cell.state = 0
        # for (z, x, y), cell in np.ndenumerate(self.cortex):
        #     cell.state = np.random.poisson(0.1)

        # pre_states = [cell.state for cell in self.cortex.flat]
        pre_states = np.random.poisson(0.01, 625)
        self.W = np.array([wi.str for wi in self.cell.syn_in])
        input = sum(self.W * pre_states)
        # print input
        if self.cell.u == 60:  # plot spikes
            self.cell.u = 0
        self.cell.u = self.cell.u - (self.cell.u - input)/self.cell.tau_u   # tau
        if self.cell.u > 30:
            self.cell.u = 60
            self.cell.state = 1
            self.cell.f += 1


            # self.raster_data[0][self.t] = 1
        # for i in range(625):
        #     self.raster_data[i][self.t] = pre_states[i]
        # Selfish
        self.cell.prp += (1000 * self.cell.state - self.cell.prp)/self.cell.tau_prp
        for syn in self.cell.syn_in:
            syn.tag += (1000 * pre_states[syn.pre.index] - syn.tag)/self.cell.tau_tag


        # STDP
        # self.STDP()

    # for (x, y, z), cell in np.ndenumerate(self.cortex):
    #     self.cell_states[x, y, z] = [220, 220, 220-int(cell.state2), 250]
    #     if not cell.state2%100 and cell.state2:
    #         self.raster_data[num][self.t] = 1
    #
    #     cell.state = cell.state2
    #     num += 1

    def STDP(self):
        if self.cell.stdp > 0.05:
                self.cell.stdp *= 0.95  # correspond to tau = 20ms, see izhikevich polychronisation
        else:
                self.cell.stdp = 0
        if self.cell.state == 1:
            self.cell.stdp = 0.1
            # potentiation
            for syn in self.cell.syn_in:
                syn.str += syn.pre.stdp

        for syn in self.cell.syn_in:
                syn.str += 0.001
        for (z, x, y), cell in np.ndenumerate(self.cortex):
            cell.state = np.random.poisson(0.1)
            # STDP
            if cell.state > 0:
                cell.stdp = 0.1
                for syn in cell.syn_out:
                    # depression
                    syn.str -= 1.8*syn.post.stdp
            if cell.stdp > 0.05:
                cell.stdp *= 0.95  # correspond to tau = 20ms, see izhikevich polychronisation
            else:
                cell.stdp = 0

    def set_syn_out(self, cell, connection = []):
        cell.syn_out = []      ##  clear all connections
        cell.syn_out += connection

    def add_syn_out(self, cell, connection=[]):
        cell.syn_out += connection

    def add_syn_in(self, cell, connection=[]):
        cell.syn_in.append(connection)


if __name__ == '__main__':
    from plot_cell import PlotWin, show_plot
    c = Cortex(dimension=(1, 1, 625))
    # graph = PlotWin(cortex=c, cell=c.cell, data='prp')
    # graph.start_timer()
    # show_plot()

    foo = c.live
    print timeit.timeit('c.live()', "from __main__ import c", number=1000)


    # for i in range(3000):
    #     c.live()
    # for ith, trial in enumerate(c.raster_data):
    #     plt.vlines(np.nonzero(trial), ith, ith + 1, color='k')
    # plt.ylim(0, 625)
    # plt.xlim(0, 1000)
    # plt.title('Example raster plot')
    # plt.xlabel('time')
    # plt.ylabel('trial')
    # plt.show()
