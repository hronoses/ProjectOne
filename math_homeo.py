import numpy as np

t = 3000                    # time of measurements
freq = 101.                    # frequency
t_f = np.arange(t*freq)/freq  # spike times in sec
tau = 1
d = [np.exp(-(t-t_i)/tau) for t_i in t_f]
print sum(d)
# v = [val/(1+sum(d[:i])) for i, val in enumerate(d)]
# print sum(v)



# problem that if i will add to rate trace +1 each time, the solution goes to infinity with time at any frequency


# not math

from brian2 import *
eqs_inputs = '''
dp_h/dt = -p_h/tau_p_h : 1                         # spike trace
rates : Hz                                              # input rates
'''

stimulus = NeuronGroup(1, eqs_inputs,
                       threshold='rand()<rates*dt',
                       # reset='p_h += 1/(1+p_h)',
                       reset='p_h += 1',
                       name='input',
                       method='linear')
tau_p_h = 100*second
stimulus.p_h = 2500  # set initial state as stable
stimulus.rates =25*Hz

post = StateMonitor(stimulus, True, record=0)

##############
#Simulaion params
#############
@network_operation(dt=50*ms)
def update_input(t):
    stimulus.rates = 25*Hz
    if 5000*ms < t < 10000*ms:
        stimulus.rates = 100*Hz
    if 25000*ms < t < 40000*ms:
        stimulus.rates = 0*Hz


simulation_time = 100*second
defaultclock.dt = 1*ms
run(simulation_time, report='text')
#

fig = figure(facecolor='white')
plot(post.t/ms, post.p_h[0])
xlabel('Time (ms)')
ylabel('p')
show()

print post.p_h[0][-1]
