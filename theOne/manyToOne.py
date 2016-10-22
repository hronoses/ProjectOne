from brian2 import *

# Neuron Model
eqs = '''
dv/dt = (gleak*(V_rest-v) + I_syn)/C: volt      # voltage
I_syn = g_ampa*(E_AMPA-v): amp                          # synaptic current
dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate
dp_h/dt = -p_h/tau_p_h : 1                    # long average homeostatic firing rate
M:1                                                     # modulation factor
'''

eqs_inputs = '''
dx_trace/dt = -x_trace/taux :1                          # spike trace
dx_s/dt = -x_s/taux_s :1                          # spike trace
rates : Hz                                              # input rates
'''

Syn_model = '''
dw/dt =  (w_s-w)/tau_w + x_trace_pre*p*(w_max > w_s)/tau_hebb : 1
dw_s/dt = (w-w_s)*M*1/tau_w_s +  w_s*(1-p_h/A)/tau_w_homeo : 1
'''
#
Pre_eq = '''
g_ampa_post += w*ampa_max_cond
w = clip(w, 0, inf)
w_s = clip(w_s, 0, inf)
'''

N_input = 100

stimulus = NeuronGroup(N_input, eqs_inputs,
                       threshold='rand()<rates*dt',
                       reset='x_trace += 1; x_s += 1')
output_neuron = NeuronGroup(1,  eqs, threshold='v>V_thr', reset='v=V_rest; p += 1; p_h += 1')


S = Synapses(stimulus, output_neuron, Syn_model, on_pre=Pre_eq)
S.connect(i=range(N_input), j=0)


################
# Neuron Params
############
V_rest = -70.*mV
V_thr = -55.*mV
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA
ampa_max_cond = 5.e-8*siemens
tau_p = 50*ms
tau_p_h = 100*second
taux = 10*ms
taux_s = 1*second
A = 10/(tau_p/second)     # 10 Hz is target firing rate. divided by tau to make A comperable to p
#################
# Plasticity params
##################
tau_w = 1
tau_w_s= 10
tau_w_homeo = 10000    # learning rate
tau_hebb = 100    # learning rate
w_max = 5
################
# Init params
#############
stimulus.rates = 1*Hz
output_neuron.p = 0
output_neuron.p_h = A   # set initial state as stable
output_neuron.M =1
w_init = 0.2
S.w = w_init   # init weight
S.w_s = w_init   # init weight

##############
# Input patterns
##################
import text_sense as ts
text = ts.TextSense(N_input)
schedule = []
schedule = text.get_schedule('starssinsgssmulstsons'*2, 500, 100, 40)
schedule += text.get_schedule('e', 10000, 100, 100)
# schedule += text.get_schedule('s', 18000, 400, 50)
# schedule += text.get_schedule('b', 1000, 100, 40)
# schedule += text.get_schedule('b', 1000, 100, 40)
# schedule += text.get_schedule('c', 2000, 100, 40)
# schedule += text.get_schedule('d', 3000, 100, 40)
# schedule += text.get_schedule('abra', 6000, 100, 40)

@network_operation(dt=50*ms)
def update_input(t):
    stimulus.rates = 1*Hz
    output_neuron.M = 1
    # if 10000*ms < t < 10150*ms:
    #     output_neuron.M = 100
    # if 5000*ms < t < 7000*ms:
    #     stimulus.rates = 0*Hz
    for i in schedule:
        if i[0] <= t/ms < i[1]:
            stimulus.rates.set_item(text.get_neurons_for(i[2]), i[3]*Hz)

############
# Connect monitors
##############
spikemon = SpikeMonitor(output_neuron)
v_Mtr = StateMonitor(output_neuron, ('v','p','p_h'), record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=10)
w_Mtr = StateMonitor(S, ('w', 'w_s'), record=True, dt=50*ms)

##############
#Simulaion params
#############
simulation_time = 20*second
defaultclock.dt = 1*ms
run(simulation_time, report='text')



def plot_state(monitor, variable, neuron=0, pre_neuron=0):
    t = range(len(monitor))
    y = range(len(monitor))
    fig = figure(facecolor='white')
    for i, m in enumerate(monitor):
        t[i] = m.t/ms
        if variable[i] == 'v':
            y[i] = m.v[neuron]
        elif variable[i] == 'p':
            y[i] = m.p[neuron]
        elif variable[i] == 'p_h':
            y[i] = m.p_h[neuron]
        elif variable[i] == 'w':
            y[i] = m.w[pre_neuron]
        elif variable[i] == 'w_s':
            y[i] = m.w_s[pre_neuron]
        elif variable[i] == 'A':
            y[i] = m.A[neuron]
        elif variable[i] == 'x_trace':
            y[i] = m.x_trace[neuron]
        else:
            print 'wrong variable'
            return 'wrong variable'
        subplot(len(monitor), 1, i+1)
        plot(t[i], y[i], '-b', label='Neuron' + variable[i])
        ax = gca()
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.ticklabel_format(useOffset=False)
        # xlabel('Time (ms)')
        ylabel(variable[i])
        # ylim(ymax = max(y[i])+2, ymin = 0)
    fig.text(0.5, 0.04, 'Time (ms)', ha='center', va='center')
    show()



def plot_spikes():
    print 'Spikes per second '+str(len(spikemon.t)/simulation_time/Hz)
    # for t in spikemon.t:
    #     axvline(t/ms, ls='-', c='r', lw=1)
    # show()


print spikemon.num_spikes
# plot_state([v_Mtr, x_trace_Mtr, w_Mtr, w_Mtr], ['p', 'x_trace', 'w', 'w_s'])
plot_state([v_Mtr,v_Mtr,  w_Mtr, w_Mtr], ['p', 'p_h', 'w', 'w_s'], pre_neuron=36)

figure(facecolor='white')
imshow(w_Mtr.w[:])
colorbar()
xlabel('time')
ylabel('w')
title('Synaptic weight')
show()
plot_spikes()

# hist(x_distrib,normed=True)
# show()