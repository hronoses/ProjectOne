from brian2 import *

'''

Inhibitory              ************                local to exc
Excitory       *********************************    local to exc and inh. random distal to exc
Input Poisson          ************                local to excitory

Neuron model: LIF
Synapse model: spike increases g_ampa, no_plasticity
'''


eqs_neurons = '''
    dv/dt = (gleak*(V_rest-v) + I_ext + I_syn)/C: volt      # voltage
    I_ext : amp                                             # external current
    I_syn = g_ampa*(E_AMPA-v): amp                          # synaptic current
    dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
    dp/dt = -p/tau_p : 1                    # (+ S_i) average firing rate
    dp_h/dt = -p_h/tau_p_h : 1                    # long average homeostatic firing rate
    dx_trace/dt = -x_trace/taux :1                          # spike trace
'''


eqs_inputs = '''
    dx_trace/dt = -x_trace/taux :1                          # spike trace
    rates : Hz                                              # input rates
'''

Syn_model =('''
            dw/dt =  (w_s-w)/tau_w + x_trace_pre*p*(w_max > w_s)/tau_hebb : 1
dw_s/dt = (w-w_s)/tau_w_s +  w_s*(1-p_h/A)/tau_w_homeo : 1
            ''')

Pre_eq = ('''
        g_ampa_post += w*ampa_max_cond
        w = clip(w, 0, inf)
        w_s = clip(w_s, 0, inf)                                                           # increment synaptic conductance
            ''')

Post_eq = ('''
            w_plus = A_LTP*x_trace_pre*(v_lowpass2_post/mV - Theta_low/mV)*(v_lowpass2_post/mV - Theta_low/mV > 0)  # synaptic potentiation
            w_ampa = clip(w_ampa+w_plus,0,w_max)                                                                    # hard bounds
            ''')


# Creating network
N_exc = 500
N_inh = 125
N_input = 100
print 'Creating NeuronGroups ... '
neurons = NeuronGroup(N_exc+N_inh, eqs_neurons, threshold='v>V_thresh',
                      reset='v=V_rest',
                      method='euler')

excitory = neurons[:N_exc]
inhibitory = neurons[N_exc:N_exc + N_inh ]

input = NeuronGroup(N_input, eqs_inputs, threshold='rand()<rates*dt',
                    method='linear')

# Crating connections
print 'Creating Synapses ... '
stimE = Synapses(input, excitory,
                 model=Syn_model,
                 on_pre=Pre_eq,
                 )
IE = Synapses(inhibitory, excitory,
              model=Syn_model,
              on_pre=Pre_eq,
              )

EI = Synapses(excitory, inhibitory,
              model=Syn_model,
              on_pre=Pre_eq,
              )

EE_local = Synapses(excitory, excitory,
                    model=Syn_model,
                    on_pre=Pre_eq,
                    )
EE_distal = Synapses(excitory, excitory,
                     model=Syn_model,
                     on_pre=Pre_eq,
                     )

print 'Connecting Synapses ... '
stimE.connect(condition='abs(5*i-j)<=15')
# IE.connect(condition='abs(5*i-j)<=2')
# EI.connect(condition='abs(i-5*j)<=2')
EE_local.connect(condition='abs(i-j)<=4')
EE_distal.connect(p=0.05)

## Neural Dynamics
V_rest = -70.*mV        # resting potential
V_thresh = -55.*mV      # spiking threshold
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA

input.rates = 50*Hz
excitory.v = V_rest
excitory.I_ext = 0.*amp
excitory.v = V_rest

#Plasticity

ampa_max_cond = 1.e-8*siemens
tau_p = 50*ms
tau_p_h = 100*second
taux = 10*ms
A = 10/(tau_p/second)     # 10 Hz is target firing rate. divided by tau to make A comperable to p
tau_w = 1
tau_w_s= 10
tau_w_homeo = 10000    # learning rate
tau_hebb = 100    # learning rate

w_max = 5
w_init = 0.5
inh_init_weight = 0

stimE.w = w_init
stimE.w_s = w_init
IE.w = -inh_init_weight
EI.w = inh_init_weight
EE_local.w = w_init/5
EE_local.w_s = w_init/5
EE_distal.w = w_init/2
EE_distal.w_s = w_init/2



defaultclock.dt = 1.*ms
final_t = 10*second
print 'Start ... '
M = SpikeMonitor(excitory)
run(final_t, report='text')




plot(M.t/ms, M.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron`s index')
show()