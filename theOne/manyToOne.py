from brian2 import *

# Neuron Model
eqs = '''
dv/dt = (gleak*(V_rest-v) + g_ampa*(E_AMPA-v))/C: volt      # voltage
dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate
dp_h/dt = -p_h/tau_p_h : 1                    # long average homeostatic firing rate

'''

eqs_inputs = '''
dx_trace/dt = -x_trace/taux :1                          # spike trace
dx_s/dt = -x_s/taux_s :1                          # spike trace
rates : Hz                                              # input rates
'''

# Syn_model = '''
# da/dt = -a : 1
# dw/dt =(w_s-w)/tau_w + x_trace_pre*p*(a-w_s)*(w_max > w_s)/tau_hebb : 1
# dw_s/dt =(w-w_s)*1*1/tau_w_s +  w_s*(1-p_h/A)/tau_w_homeo : 1
# '''
Syn_model = '''
dw/dt =(w_s-w)/tau_w + x_trace_pre*p*(w_max > w_s)/tau_hebb : 1
dw_s/dt =(w-w_s)*1*1/tau_w_s +  w_s*(1-p_h/A)/tau_w_homeo : 1
'''

Pre_eq = '''
g_ampa_post += w*ampa_max_cond

w = clip(w, 0, inf)
w_s = clip(w_s, 0, inf)
'''
#a += p + x_trace_pre*p
N_input = 100

stimulus = NeuronGroup(N_input, eqs_inputs,
                       threshold='rand()<rates*dt',
                       reset='x_trace += 1; x_s += 1',
                       name='input',
                       method='linear')
output_neuron = NeuronGroup(1,  eqs, threshold='v>V_thr', reset='v=V_rest; p += 1; p_h += 1/(p_h+0.1)',
                            name='post_neuron',
                            method='euler'
                            )
# p_h increases after each spike by a low value, it is important, otherwise brief burst of spikes will change p_h
# dramatically and it will elicit strong homeo effect only after single burst
# added 0.1 to prevent blow up if p_h goes to 0


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
A = 1/(tau_p/second)     # 10 Hz is target firing rate. divided by tau to make A comperable to p
print 'A=' + str(A)

output_neuron.p = 0
output_neuron.p_h = A   # set initial state as stable
# output_neuron.M = 1
#################
# Plasticity params
##################
tau_w = 5*second
tau_w_s= 10*tau_w
tau_w_homeo = 1000    # learning rate
tau_hebb = 100    # learning rate
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
schedule += text.get_schedule('sss', 100, 100, 40)
# schedule += text.get_schedule('ssasdfcaewaewfdsgaehawfsasasdfadsffsagvcbhgjikddfs', 5000, 100, 40)

@network_operation(dt=50*ms)
def update_input(t):
    stimulus.rates = 1*Hz
    # output_neuron.M = 1
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
post = StateMonitor(output_neuron, True, record=0)
x_trace_Mtr = StateMonitor(stimulus, 'x_trace', record=range(100))
syn = StateMonitor(S, True, record=True, dt=50*ms)

##############
#Simulaion params
#############
simulation_time = 50*second
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
subplot(2, 1, 1)
plot(post.t/ms, post.p[0], '-b', label='p')
plot(post.t/ms, post.p_h[0], '-r', label='p_h')
xlabel('Time (ms)')
legend(loc='upper right')
subplot(2, 1, 2)
ax = gca()
ax.get_yaxis().get_major_formatter().set_scientific(False)
ax.ticklabel_format(useOffset=False)
plot(syn.t/ms, syn.w[pre_neuron], '-b', label='w')
plot(syn.t/ms, syn.w_s[pre_neuron], '-r', label='w_s')
xlabel('Time (ms)')
legend(loc='upper right')
show()

figure(facecolor='white')
imshow(syn.w_s[:], cmap="gist_yarg", interpolation='nearest', aspect='auto')
colorbar(format='%.5f')
# xticks(np.arange(20)*50, fontsize=9)
xlabel('time')
ylabel('w')
title('Synaptic weight')
show()


# hist(x_distrib,normed=True)
# show()