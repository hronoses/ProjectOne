import string
import numpy as np
import itertools
import pickle


class TextSense:
    def __init__(self, neuron_num):
        self.vocabulary = ' '
        self.vocabulary += string.ascii_lowercase
        self.vocabulary += '-'
        self.vocNum = dict(zip(range(len(self.vocabulary)), self.vocabulary))
        self.vocLet = dict(zip(self.vocabulary, range(len(self.vocabulary))))
        self.datafile = 'features_data.p'
        try:
            with open(self.datafile) as file:
                data = pickle.load(file)
                self.features = data['features']
                self.patterns = data['patterns']
                self.total_num_patterns = data['total_num_patterns']
                if self.total_num_patterns != neuron_num:
                    raise 'error'
        except:
            self.num_features = 5   # features per latter
            self.total_num_features = 100   # total number of features
            self.num_patterns = 10   # patterns per feature
            self.total_num_patterns = neuron_num    # number of neurons
            self.features = self.gen_features()
            self.patterns = self.gen_patterns()
            with open(self.datafile, 'wb') as file:
                pickle.dump({'features': self.features, 'patterns': self.patterns, 'total_num_patterns': neuron_num}, file)

    def sense(self, data=' '):
        return self.vocLet[data]

    def gen_features(self):
        n = len(self.vocabulary)
        f = [np.random.randint(1, self.total_num_features, self.num_features) for _ in range(n)]
        return dict(zip(self.vocabulary, f))

    def gen_patterns(self):
            n = self.total_num_features
            f = [np.random.randint(1, self.total_num_patterns, self.num_patterns) for _ in range(n)]
            return dict(zip(range(self.total_num_features), f))

    def get_neurons_for(self, latter=' '):
        return list(itertools.chain.from_iterable([self.patterns[i] for i in self.features[latter]]))

    def get_schedule(self, word, start_time, time_duration):
        time = [[0, 0, '']] * len(word)   # [start time, end time, latter]
        time[0] = [start_time, start_time + time_duration, 's']
        for i, latter in enumerate(word[1:]):
            prev = time[i][1]
            time[i+1] = [prev, prev + time_duration, latter]
        return time

if __name__ == '__main__':
    t = TextSense(100)
    # print t.vocLet
    # print t.sense()
    # print t.features['s']
    # print t.patterns[5]
    print t.get_schedule('synapse', 100,50)