from brian2 import *

# Neuron Model
eqs_inputs = '''
dp/dt = -p/tau_p :1                          # spike trace
rates : Hz                                              # input rates
'''


stimulus = NeuronGroup(1, eqs_inputs,
                       threshold='rand()<rates*dt',
                       reset='p += 1')

# Neuron Params
tau_p = 100*ms
stimulus.rates = 10*Hz

# Connect monitors
spikemon = SpikeMonitor(stimulus)
v_Mtr = StateMonitor(stimulus, 'p', record=0)


#Simulaion params
simulation_time = 20*second
defaultclock.dt = 1*ms                        # timestep

run(simulation_time, report='text')


def create_t(tau, total_time):
    time = [[0, 0]] * int(total_time/tau)
    time[0] = [0, 0 + tau]
    for i in range(int(total_time/tau)-1):
        prev = time[i][1]
        time[i+1] = [prev, prev + tau]
    return time

def plot_spikes():
    print 'Spikes per second '+str(len(spikemon.t)/simulation_time/Hz)
    spikes = spikemon.t/ms
    # for i,s in enumerate(spikes[1:]):
    #     print spikes[i]-spikes[i-1]
    mean_rate = np.zeros((2, 20000/100))
    for i, t in enumerate(create_t(100, 20000)):
        mean_rate[0, i] = t[1]
        mean_rate[1, i] = np.where((spikes >= t[0]) & (spikes <= t[1]))[0].size
    plot(mean_rate[0], mean_rate[1], '-b', label='<S>')
    plot(v_Mtr.t/ms, v_Mtr.p[0], '-r', label='p')
    xlabel('time')
    ylabel('mean firing rate')
    legend(loc='upper right')
    show()

# print spikemon.num_spikes
plot_spikes()
