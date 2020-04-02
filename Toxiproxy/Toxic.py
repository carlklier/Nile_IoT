class Toxic:
    name = None
    type = None
    stream = 'downstream'  # default
    toxicity = 1.0  # probability of the toxic being applied to a link (defaults to 1.0, 100%)

    def __init__(self, n, t, s, to):
        self.name = n
        self.type = t
        self.stream = s
        self.toxicity = to

    def set_name(self, n):
        self.name = n

    def set_type(self, t):
        self.type = t

    def set_stream(self, s):
        self.stream = s

    def set_toxicity(self, to):
        self.toxicity = to




