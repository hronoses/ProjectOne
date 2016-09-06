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
dw/dt =  0* (((w+1/w)*(((A-p))**1))/tau_w_homeo + (((p-A))*x_trace_pre)/tau_w_hebb)  : 1
'''

# (w)*(w>=0.1)*

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
# tau_m = 10*ms
tau_p = 100*ms
tau_A = 1*second
V_rest = -70.*mV
V_thr = -55.*mV


taux = 1000*ms
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA
ampa_max_cond = 5.e-8*siemens

A = 20

w_max = 5
tau_w_homeo = 1000    # learning rate
tau_w_hebb = 1000    # learning rate
# Init params
w_init = 0.1

S.w = w_init   # init weight
stimulus.rates = 50*Hz

import text_sense as ts
input_word = 'sssss'
text = ts.TextSense(N_input)
schedule = []
schedule = text.get_schedule(input_word, 500, 200, 60)
# schedule += text.get_schedule('sssss', 6000, 200, 15)
x_distrib = []

@network_operation(dt=50*ms)
def update_input(t):
    global x_distrib
    stimulus.rates = 10*Hz
    # if 1000*ms < t < 2000*ms:
    #     stimulus.rates = 80*Hz
    # if 5000*ms < t < 7000*ms:
    #     stimulus.rates = 0*Hz
    for i in schedule:
        if i[0] <= t/ms <= i[1]:
            stimulus.rates.set_item(text.get_neurons_for(i[2]), i[3]*Hz)
    x_distrib.append(stimulus.x_trace[5])
    # print stimulus.rates


# Connect monitors
spikemon = SpikeMonitor(output_neuron)
v_Mtr = StateMonitor(output_neuron, ('v','p'), record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=10)
w_Mtr = StateMonitor(S, 'w', record=True, dt=50*ms)


#Simulaion params
simulation_time = 20*second
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
        # ylim(ymax = max(y[i])+2, ymin = 0)
    show()

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
    for i,s in enumerate(spikes[1:]):
        print spikes[i]-spikes[i-1]
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
# plot_state([v_Mtr, x_trace_Mtr, w_Mtr], ['p', 'x_trace', 'w'])
#
# for i in range(99):
#     plot(w_Mtr.t/ms, w_Mtr.w[i], '-b', label='Str')
# show()
#
# imshow(w_Mtr.w[:])
# xlabel('time')
# ylabel('w')
# title('Synaptic weight')
# show()
plot_spikes()
# hist(x_distrib,normed=True)
# show()