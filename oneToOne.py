'''
One to One connection of two neuron
IF                      *
poisson input           *
Simple stable model of Plasticity
if stimulus rate changes weight also changes to compensate low input
No Hebbian learning

'''

from brian2 import *

# Neuron Model
eqs = '''
dv/dt = (gleak*(V_rest-v) + I_ext + I_syn)/C: volt      # voltage
I_ext : amp                                             # external current
I_syn = g_ampa*(E_AMPA-v): amp                          # synaptic current
dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate


'''


eqs_inputs = '''
dx_trace/dt = -x_trace/taux :1                          # spike trace
rates : Hz                                              # input rates
'''

Syn_model = '''
dw/dt = w*(A-p)/tau_w : 1

'''

Pre_eq = '''
g_ampa_post += w*ampa_max_cond
w = clip(w, 0, inf)
'''
Post_eq = ('''
p += 1

''')

BCM_model = '''
dw/dt = p*(p - A)*x_trace_pre : 1
'''

stimulus = NeuronGroup(1, eqs_inputs, threshold='rand()<rates*dt', reset='x_trace += 1')
output_neuron = NeuronGroup(1,  eqs, threshold='v>V_thr', reset='v=V_rest')

S = Synapses(stimulus, output_neuron, Syn_model, on_pre=Pre_eq, on_post=Post_eq)
S.connect(j='0')

# Neuron Params
tau_m = 10*ms
tau_p = 1000*ms
tau_A = 1*second
V_rest = -70.*mV
V_thr = -55.*mV

A = 20   # target level of neuron activation

taux = 50*ms
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA

ampa_max_cond = 5.e-8*siemens  # Ampa maximal conductance
w_max = 50
tau_w = 100    # learning rate

# initial params
stimulus.rates = 40*Hz
w_init = 2
S.w = w_init   # init weight


#Simulaion params
simulation_time = 20*second
defaultclock.dt = 1*ms                        # timestep


@network_operation(dt=50*ms)
def update_input(t):
    stimulus.rates = 20*Hz
    if 1000*ms < t < 2000*ms:
        stimulus.rates = 80*Hz
    if 5000*ms < t < 7000*ms:
        stimulus.rates = 0*Hz



# Connect monitors
spikemon = SpikeMonitor(output_neuron)
v_Mtr = StateMonitor(output_neuron, 'v', record=0)
p_Mtr = StateMonitor(output_neuron, 'p', record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=0)
w_Mtr = StateMonitor(S, 'w', record=0)


run(simulation_time, report='text')


def plot_state(monitor, variable, neuron=0):
    t = range(len(monitor))
    y = range(len(monitor))
    for i, m in enumerate(monitor):
        t[i] = m.t/ms
        if variable[i] == 'v':
            y[i] = m.v[neuron]
        elif variable[i] == 'p':
            y[i] = m.p[neuron]
        elif variable[i] == 'w':
            y[i] = m.w[neuron]
        elif variable[i] == 'A':
            y[i] = m.A[neuron]
        elif variable[i] == 'x_trace':
            y[i] = m.x_trace[neuron]
        else:
            print 'wrong variable'
            return 'wrong variable'
        subplot(len(monitor), 1, i+1)
        plot(t[i], y[i], '-b', label='Neuron' + variable[i])
        xlabel('Time (ms)')
        ylabel(variable[i])
    show()


def plot_spikes():
    for t in spikemon.t[:100]:
        axvline(t/ms, ls='-', c='r', lw=1)
    show()




plot_state([p_Mtr, x_trace_Mtr, w_Mtr], ['p', 'x_trace', 'w'])
# plot_state([v_Mtr], ['v'])
# plot_spikes()
# print spikemon.count
