import numpy as np
import matplotlib.pyplot as plt

def plot_graph(**kwargs):
    A = kwargs['A']
    w=kwargs['w']
    tau_H = kwargs['tau_w_homeo']
    tau_Hebb = kwargs['tau_w_hebb']


if __name__ == '__main__':
    tau_w_homeo = 1000    # learning rate
    tau_w_hebb = 1000
    A = 70
    w = 0.5
    x = 5
    beta = 7
    # print plot_graph(A=A, w=w, tau_w_homeo=tau_w_homeo, tau_w_hebb=tau_w_hebb)
    p = np.arange(0,150,0.1)
    dw = np.zeros(p.shape)
    plt.figure(facecolor='white')
    for i in range(10):
        w=0.1*(i+1)
        dw = (w*(((A-p)/beta)**3))/tau_w_homeo + (((p-A))*x)/tau_w_hebb
        plt.plot(p, dw, label='w='+str(w))
    # dw = ((((A-p)/beta)**3))/tau_w_homeo + (((p-A))*x)/tau_w_hebb
    # plt.plot(p, dw)
    plt.legend()
    plt.axhline(0, color='red')
    plt.show()
    # print dw