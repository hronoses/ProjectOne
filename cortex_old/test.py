import numpy as np
import matplotlib.pyplot as plt


def raster(event_times_list, color='k'):
    """
    Creates a raster plot
    Parameters
    ----------
    event_times_list : iterable
                       a list of event time iterables
    color : string
            color of vlines
    Returns
    -------
    ax : an axis containing the raster plot
    """
    ax = plt.gca()
    for ith, trial in enumerate(event_times_list):
        plt.vlines(trial, ith + .5, ith + 1.5, color=color)
    plt.ylim(.5, len(event_times_list) + .5)
    return ax

if __name__ == '__main__':
    # example usage
    # Generate test data
    nbins = 100
    ntrials = 10
    spikes = []
    for i in range(ntrials):
        spikes.append(np.arange(nbins)[np.random.rand(nbins) < .2])

    # fig = plt.figure()
    # ax = plt.gca()

    data = np.eye(10).reshape((5,20))
    # print np.arange(10) * data
    # data[1][3] = 1
    for ith, trial in enumerate(data):
        # print ith, trial
        plt.vlines(np.nonzero(trial), ith + .5, ith + 1.5, color='k')
    # plt.ylim(.5, len(spikes) + .5)
    plt.ylim(0, 10)
    plt.xlim(0, 20)
    plt.title('Example raster plot')
    plt.xlabel('time')
    plt.ylabel('trial')
    plt.show()