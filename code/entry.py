class Entry(object):
    def __init__(self):
        self.counts = []
        self.words = []
        self.words_full = []

        # imitate recordclass functionality:
        self.__fields__ = ["counts", "words", "words_full"]

