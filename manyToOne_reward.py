from brian2 import *

# Neuron Model
eqs = '''
dv/dt = (gleak*(V_rest-v) + g_ampa*(E_AMPA-v))/C: volt      # voltage
dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate
dp_slow/dt = -p/tau_p_slow : 1                    # (+ S_i) average firing rate
dp_h/dt = -p_h/tau_p_h : 1                    # long average homeostatic firing rate
dy/dt = -y/tau_y : 1                    # long average homeostatic firing rate
M:1
'''

eqs_inputs = '''
dx_trace/dt = -x_trace/taux :1                          # spike trace
dx_s/dt = -x_s/taux_s :1                          # spike trace
rates : Hz                                              # input rates
'''

Syn_model = '''
dw/dt =(w_s-w)/tau_w: 1
dw_s/dt =(w-w_s)*M/tau_w_s +  w_s*(1-p_h/A)**3/tau_w_homeo : 1
'''

Pre_eq = '''
g_ampa_post += w*ampa_max_cond
w -= p/1000
w = clip(w, 0, inf)
w_s = clip(w_s, 0, inf)
'''
Post_eq = '''
w += p_slow*x_trace_pre/1000
w = clip(w, 0, inf)
w_s = clip(w_s, 0, inf)
'''
#a += p + x_trace_pre*p
N_input = 100

stimulus = NeuronGroup(N_input, eqs_inputs,
                       threshold='rand()<rates*dt',
                       reset='x_trace = 1; x_s += 1',
                       name='input',
                       method='linear')
output_neuron = NeuronGroup(1,  eqs, threshold='v>V_thr', reset='v=V_rest; p = 1; p_slow = 1;y += 1; p_h += 1',
                            name='post_neuron',
                            method='euler'
                            )
# p_h increases after each spike by a low value, it is important, otherwise brief burst of spikes will change p_h
# dramatically and it will elicit strong homeo effect only after single burst
# added 0.1 to prevent blow up if p_h goes to 0


S = Synapses(stimulus, output_neuron, Syn_model, on_pre=Pre_eq, on_post=Post_eq,method='euler')
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
tau_p = 20*ms
tau_p_slow = 100*ms
tau_p_h = 10*second
tau_y = 1000*ms
taux = 20*ms
taux_s = 1*second
A = 10*(tau_p_h/second)     # 10 Hz is target firing rate.
print 'A=' + str(A)

stimulus.x_trace = 0
output_neuron.M = 1
output_neuron.p = 0
output_neuron.p_slow = 0
output_neuron.p_h = A   # set initial state as stable
# output_neuron.M = 1
#################
# Plasticity params
##################
tau_w = 2*second
tau_w_s= 5*tau_w
# temporally exclude homeo to test triplet rule
tau_w_homeo = 200*second    # learning rate
tau_hebb = 70*ms    # learning rate
w_max = 5

stimulus.rates = 1*Hz

w_init = 0.25
S.w = w_init   # init weight
S.w_s = w_init   # init weight
#S.a = 1

##############
# Input patterns
##################
import text_sense as ts
text = ts.TextSense(N_input)
schedule = []
schedule = text.get_schedule(' ', 1, 1, 1)
# word = 'ssasdfcsessasewfdsgaeshawssssdfadsssagvscbhssgjiskdfs'
# schedule += text.get_schedule(word, 100, 100, 20)
freq = 60
schedule += text.get_schedule('q', 1000, 400, freq)
schedule += text.get_schedule('f', 2000, 400, freq)
schedule += text.get_schedule('s', 9800, 400, freq)
print schedule

@network_operation(dt=50*ms)
def update_input(t):
    stimulus.rates = 1*Hz
    if 10100*ms < t < 10200*ms:
        output_neuron.M = 1000
    else:
        output_neuron.M = 1
#     # output_neuron.M = 1
#     # if 10000*ms < t < 10150*ms:
#     #     output_neuron.M = 100
#     # if 5000*ms < t < 7000*ms:
#     #     stimulus.rates = 0*Hz
    ### it is very ineficient code/ it loops every dt in entire schedule
    for i in schedule:
        if i[0] <= t/ms < i[1]:
            stimulus.rates.set_item(text.get_neurons_for(i[2]), i[3]*Hz)

############
# Connect monitors
##############
spikemon = SpikeMonitor(stimulus)
post_spike = SpikeMonitor(output_neuron)
post = StateMonitor(output_neuron, ('y', 'p_h'), record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=range(100))
syn = StateMonitor(S, True, record=True, dt=1*ms)

##############
#Simulaion params
#############
simulation_time = 30*second
defaultclock.dt = 1*ms
run(simulation_time, report='text')



def plot_spikes():
    print 'Spikes per second '+str(len(spikemon.t)/simulation_time/Hz)
    # for t in spikemon.t:
    #     axvline(t/ms, ls='-', c='r', lw=1)
    # show()


print 'Total spikes: ' + str(spikemon.num_spikes)
plot_spikes()



pre_neuron = text.get_neurons_for('s')[0]

fig = figure(facecolor='white')
num_plot = 3
# subplot(num_plot, 1, 1)
# plot(spikemon.t/ms, spikemon.i, '.k')
# plot(post_spike.t/ms, post_spike.i, 'ro')
# xlabel('Time (ms)')
# ylabel('Neuron index')
subplot(num_plot, 1, 1)
plot(post.t/ms, post.y[0], '-b', label='y')
ylabel('y')
# ylim([0,10])
# legend(loc='upper right')
subplot(num_plot, 1, 2)
plot(post.t/ms, post.p_h[0], '-r', )
# xlabel('Time (ms)')
ylabel('ys')
# legend(loc='upper right')
subplot(num_plot, 1, 3)
ax = gca()
ax.get_yaxis().get_major_formatter().set_scientific(False)
ax.ticklabel_format(useOffset=False)
plot(syn.t/ms, syn.w[pre_neuron], '-b', label='w')
plot(syn.t/ms, syn.w_s[pre_neuron], '-r', label='ws')
xlabel('Time (ms)')
legend(loc='upper right')
show()

figure(facecolor='white')

imshow(syn.w_s[:], cmap="gist_yarg", interpolation='nearest', aspect='auto')
# plot(np.ones(len(text.get_neurons_for('s'))),text.get_neurons_for('s'),'o')
colorbar(format='%.5f')
# xticks(np.arange(20)*50, fontsize=9)
xlabel('Time (ms)')
ylabel('ws')
# title('Synaptic weight')
show()

# hist(x_distrib,normed=True)
# show()