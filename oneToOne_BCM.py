from brian2 import *

# Neuron Model
eqs = '''
dv/dt = (gleak*(V_rest-v) + I_ext + I_syn)/C: volt      # voltage
I_ext : amp                                             # external current
I_syn = g_ampa*(E_AMPA-v): amp                          # synaptic current
dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate


'''
for_BCM = '''
dA/dt = -A/tau_A : 1                    # (+ S_i) average firing rate with big tau
'''


eqs_inputs = '''
dx_trace/dt = -x_trace/taux :1                          # spike trace
rates : Hz                                              # input rates
'''

Syn_model = '''
dw/dt = A-p : 1
'''

Pre_eq = '''
g_ampa_post += w*ampa_max_cond
'''
Post_eq = ('''
p += 1
A += 1

''')

BCM_model = '''
dw/dt = p*(p - A)*x_trace_pre : 1
'''

stimulus = NeuronGroup(1, eqs_inputs, threshold='rand()<rates*dt', reset='x_trace += 1')
output_neuron = NeuronGroup(1,  eqs + for_BCM, threshold='v>V_thr', reset='v=V_rest')

S = Synapses(stimulus, output_neuron, BCM_model, on_pre=Pre_eq, on_post=Post_eq)
S.connect(j='0')

# Neuron Params
tau_m = 10*ms
tau_p = 100*ms
tau_A = 1*second
V_rest = -70.*mV
V_thr = -55.*mV

A = 5   # target level of neuron activation

taux = 50*ms
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA

ampa_max_cond = 5.e-8*siemens  # Ampa maximal conductance
w_max = 50

# initial params
output_neuron.A = 5
stimulus.rates = 100*Hz
w_init = 4
S.w = w_init   # init weight


#Simulaion params
simulation_time = 10*second
defaultclock.dt = 1*ms                        # timestep


# Connect monitors
spikemon = SpikeMonitor(output_neuron)
v_Mtr = StateMonitor(output_neuron, 'v', record=0)
p_Mtr = StateMonitor(output_neuron, 'p', record=0)
A_Mtr = StateMonitor(output_neuron, 'A', record=0)
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




# plot_state(p_Mtr, 'p')
plot_state([p_Mtr, x_trace_Mtr, A_Mtr, w_Mtr], ['p', 'x_trace', 'A', 'w'])
# plot_state(x_trace_Mtr, 'x_trace')
# plot_spikes()

# plot(x_trace_Mtr.t/ms, x_trace_Mtr.x_trace[0], '-b', label='Neuron 0')
# xlabel('Time (ms)')
# ylabel('v')
# legend(loc='best')
# show()

# subplot(2, 1, 1)
# plot(t, y, '-b', label='Neuron' + variable)
# xlabel('Time (ms)')
# ylabel(variable)