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
    x:metre
    y:metre
'''


eqs_inputs = '''
    dv/dt = gleak*(V_rest-v)/C: volt                        # voltage
    rates : Hz                                              # input rates
    # selected_index : integer (shared)                       # active neuron
'''

Syn_model =('''
            w:1                # synaptic weight (ampa synapse)
            ''')

Pre_eq = ('''
            g_ampa_post += w*ampa_max_cond                                                             # increment synaptic conductance
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
                    reset='v=V_rest',
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
IE.connect(condition='abs(5*i-j)<=2')
EI.connect(condition='abs(i-5*j)<=2')
EE_local.connect(condition='abs(i-j)<=4')
EE_distal.connect(p=0.05)

## pararms
V_rest = -70.*mV        # resting potential
V_thresh = -55.*mV      # spiking threshold
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA

ampa_max_cond = 1.e-8*siemens
# Initial values
input.rates = 50*Hz
excitory.v = V_rest
excitory.I_ext = 0.*amp
excitory.v = V_rest

init_weight = 0.5
inh_init_weight = 0

stimE.w = init_weight
IE.w = -inh_init_weight
EI.w = inh_init_weight
EE_local.w = init_weight/5
EE_distal.w = init_weight/2



defaultclock.dt = 1.*ms
final_t = 10*second
print 'Start ... '
M = SpikeMonitor(excitory)
run(final_t, report='text')




plot(M.t/ms, M.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron`s index')
show()