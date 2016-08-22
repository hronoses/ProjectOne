from brian2 import *

eqs_neurons = '''
    dv/dt = (gleak*(V_rest-v) + I_ext + I_syn)/C: volt      # voltage
    I_ext : amp                                             # external current
    I_syn = g_ampa*(E_AMPA-v): amp                          # synaptic current
    dg_ampa/dt = -g_ampa/tau_AMPA : siemens                 # synaptic conductance
    x:metre
    y:metre
'''

# input neurons
eqs_inputs = '''
dv/dt = gleak*(V_rest-v)/C: volt                        # voltage
rates : Hz                                              # input rates
# selected_index : integer (shared)                       # active neuron
'''

## pararms
V_rest = -70.*mV        # resting potential
V_thresh = -55.*mV      # spiking threshold
gleak = 30.*nS                  # leak conductance
C = 300.*pF                     # membrane capacitance
tau_AMPA = 2.*ms                # AMPA synaptic timeconstant
E_AMPA = 0.*mV                  # reversal potential AMPA

# spacial structure
cell_size = 0.05*mmetre
x_max = 100*mmeter
y_max = 100*mmeter


N_exc = 500
N_inh = 125
N_input = 100
init_weight = 0.5


excitory = NeuronGroup(N_exc, eqs_neurons, threshold='v>V_thresh',
                       reset='v=V_rest',
                       method='euler')
input = NeuronGroup(N_input, eqs_inputs, threshold='rand()<rates*dt',
                    reset='v=V_rest',
                    method='linear')



# equations executed at every timestep
Syn_model =   ('''
            w:1                # synaptic weight (ampa synapse)
            ''')

# equations executed only when a presynaptic spike occurs
Pre_eq = ('''
            g_ampa_post += w*ampa_max_cond                                                             # increment synaptic conductance
            ''' )

# equations executed only when a postsynaptic spike occurs
Post_eq = ('''
            v_lowpass1 += 10*mV                                                                                     # mimics the depolarisation effect due to a spike
            v_lowpass2 += 10*mV                                                                                     # mimics the depolarisation effect due to a spike
             v_homeo += 0.1*mV                                                                                      # mimics the depolarisation effect due to a spike
            w_plus = A_LTP*x_trace_pre*(v_lowpass2_post/mV - Theta_low/mV)*(v_lowpass2_post/mV - Theta_low/mV > 0)  # synaptic potentiation
            w_ampa = clip(w_ampa+w_plus,0,w_max)                                                                    # hard bounds
            ''' )


Syn = Synapses(input, excitory,
               model=Syn_model,
               on_pre=Pre_eq,
               # on_post=Post_eq
               )
Syn.connect(p=0.5)


ampa_max_cond = 1.e-8*siemens
# Initial values
input.rates = 20*Hz
excitory.v = V_rest
excitory.I_ext = 0.*amp
excitory.v = V_rest
Syn.w = init_weight
defaultclock.dt = 1.*ms
final_t = 1*second


M = SpikeMonitor(excitory)
run(final_t, report='text')

plot(M.t/ms, M.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron`s index')
show()