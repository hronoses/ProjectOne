from brian2 import *

# Neuron Model
eqs = '''
dy/dt = -y/tauy :1
dy2/dt = -y2/tauy2 :1
'''

eqs_inputs = '''
dx/dt = -x/taux :1                          # spike trace
dx2/dt = -x2/taux2 :1                          # spike trace
ind : 1
'''

Syn_model = '''
da/dt = -a/0.5  : 1
w  : 1
'''

Pre_eq = '''
w += y*(a-w_s)
a += y2
'''
Post_eq = '''
w += x_pre*(a-w_s)
a += x2_pre
'''
N_input = 100
Delay = 50
one = NeuronGroup(N_input, eqs_inputs, threshold='ind == int(t/ms%Delay)', reset='x=1; x2=1')
post = NeuronGroup(1, eqs, threshold='50 == int(t/ms%Delay)', reset='y=1; y2=1')

S = Synapses(one, post, Syn_model, on_pre=Pre_eq, on_post=Post_eq)
S.connect(i=range(N_input), j=0)


taux = 10*ms
tauy = 10*ms
taux2 = 5*ms
tauy2 = 50*ms
tau_hebb = 1
w_s = 2

w0 = 0.5
S.w = w0
S.a = 0

one.x = 0
# one.tmp = 0
one.ind = 'i'

post.y = 0

# @network_operation(dt=1*ms)
# def update_input(t):
#     if t == 50*ms:
#         post.y = 1

        # print
############
# Connect monitors
##############
# post = StateMonitor(output_neuron, True, record=0)
pre = StateMonitor(one, True, record=True)
syn = StateMonitor(S, True, record=True, dt=1*ms)

##############
#Simulaion params
#############
simulation_time = 10*second
defaultclock.dt = 1*ms
run(simulation_time, report='text')

# fig = figure(facecolor='white')
# plot(pre.t/ms, pre.x[10], '-b', label='p')
# xlabel('Time (ms)')
# show()


# figure(facecolor='white')
# imshow(pre.x[:], cmap="gist_yarg", interpolation='nearest', aspect='auto')
# colorbar(format='%.5f')
# xlabel('time')
# ylabel('x')
# show()
#
figure(facecolor='white')
imshow(syn.w[:], cmap="gist_yarg", interpolation='nearest', aspect='auto')
colorbar(format='%.5f')
xlabel('time')
ylabel('w')
show()

# fig = figure(facecolor='white')
# plot(syn.t/ms, syn.w[0], '-b', label='p')
# ax = gca()
# ax.get_yaxis().get_major_formatter().set_scientific(False)
# ax.ticklabel_format(useOffset=False)
# show()
y = []
for s in syn.w[:]:
    y.append(s[-1])

plot(y)
hlines(w0, 0, 100)
show()


# print pre.tmp[6]
# print pre.tmp[5]
# print post.g