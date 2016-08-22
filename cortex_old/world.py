# from cortex import *
from cortex_memory import *
from visual3do import visualize3d
import matplotlib.pyplot as plt


class TextSense():
    def __init__(self):
        self.voc = dict(zip(range(1,27), string.ascii_lowercase ))
        self.vocLet = dict(zip(string.ascii_lowercase, range(1,27)))
        self.vocLet[' '] = 0   # 0 means silence
        self.vocLet['-'] = 27

    def process(self, data):
        return [(self.vocLet[i],) for i in data]


class Environment():
    """
    just input text
    """

    def __init__(self, env_data):
        self.data = env_data


class World():
    def __init__(self, env_data=None):
        print ' Initializing TextSense'
        self.t = TextSense()
        print ' Initializing Cortex'
        self.cortex = Cortex(dimension=(1, 30, 30))
        self.dt = iter(self.t.process(env_data.lower()))
        self.data = []
        self.env_data = env_data
        self.pred_data = []

    def evolve(self):
        try:
            data = self.dt.next()
        except:
            data = None
        self.cortex.thalamus.live(data)  # it provides input to cortex
        self.cortex.live()


if __name__ == '__main__':
    print 'Initializing World ....'
    text = 'abcd'*10
    text += '     '*60
    w = World(env_data=text)
    print 'Done'
    for i in range(299):
        print 'Step: ' + str(i)
        w.evolve()
        w.data.append(np.copy(w.cortex.cell_states))
        w.pred_data.append(w.cortex.top_active)
        # print w.cortex.cortex[0,4,4].syn_in[0].str
    # print w.data
    # print w.env_data
    # print w.pred_data
    # print w.cortex.data

    # plt.plot(w.cortex.data)
    # plt.ylabel('some numbers')
    # plt.show()
    # print w.cortex.raster_data
    # nbins = 100
    # ntrials = 10
    # spikes = []
    # for i in range(ntrials):
    #     spikes.append(np.arange(nbins)[np.random.rand(nbins) < .2])

    # fig = plt.figure()
    # ax = plt.gca()
    for ith, trial in enumerate(w.cortex.raster_data):
        plt.vlines(np.nonzero(trial), ith, ith + 1, color='k')
    plt.ylim(0, 500)
    plt.xlim(0, 100)
    plt.title('Example raster plot')
    plt.xlabel('time')
    plt.ylabel('trial')
    # plt.show()
    visualize3d(w.data, env_data=w.env_data, pred_data=w.pred_data)
