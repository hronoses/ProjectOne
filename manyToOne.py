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
dw/dt =  (w*(A-p)*(w>=0))/tau_w : 1
'''
Pre_eq = '''
g_ampa_post += w*ampa_max_cond
w = clip(w, 0, inf)
'''
Post_eq = '''


'''

N_input = 100

stimulus = NeuronGroup(N_input, eqs_inputs,
                       threshold='rand()<rates*dt',
                       reset='x_trace += 1')
output_neuron = NeuronGroup(1,  eqs, threshold='v>V_thr', reset='v=V_rest; p += 1')


S = Synapses(stimulus, output_neuron, Syn_model, on_pre=Pre_eq, on_post=Post_eq)
S.connect(i=range(N_input), j=0)



# Neuron Params
tau_m = 10*ms
tau_p = 100*ms
tau_A = 1*second
V_rest = -70.*mV
V_thr = -55.*mV


taux = 50*ms
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA
ampa_max_cond = 5.e-8*siemens

A = 40

w_max = 5
tau_w = 100    # learning rate
# Init params
w_init = 1

S.w = w_init   # init weight
stimulus.rates = 50*Hz

# Generate a matrix for display
w_matrix = np.zeros((len(stimulus), 200))
w_matrix[S.i[:], 0] = S.w[:]
ind=0

input_word = 'synapse'
import text_sense as ts
text = ts.TextSense(N_input)
schedule = text.get_schedule(input_word, 100, 300)
# print stimulus.rates.get_item([4,5,2])
@network_operation(dt=50*ms)
def update_input(t):
    global ind
    stimulus.rates[10] = 1000*Hz
    stimulus.rates = 20*Hz
    # if 1000*ms < t < 2000*ms:
    #     stimulus.rates = 80*Hz
    if 5000*ms < t < 7000*ms:
        stimulus.rates = 0*Hz
    ind += 1
    try:
        w_matrix[S.i[:], ind] = S.w[:]
    except:
        pass
    for i in schedule:
        if i[0] <= t/ms <= i[1]:
            stimulus.rates.set_item(text.get_neurons_for(i[2]), 100*Hz)

# Connect monitors
spikemon = SpikeMonitor(output_neuron)
v_Mtr = StateMonitor(output_neuron, 'v', record=0)
p_Mtr = StateMonitor(output_neuron, 'p', record=0)
w_Mtr = StateMonitor(S, 'w', record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=10)

#Simulaion params
simulation_time = 10*second
defaultclock.dt = 1*ms                        # timestep

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
    for t in spikemon.t:
        axvline(t/ms, ls='-', c='r', lw=1)
    show()



plot_state([p_Mtr, x_trace_Mtr, w_Mtr], ['p', 'x_trace', 'w'])

imshow(w_matrix)
xlabel('time')
ylabel('w')
title('Synaptic weight')
show()