from typing import Dict
CSV_LOCATION = 'concreteness_ratings_brysbaert.txt'

class WordConcretenessAnalyser:

    def __init__(self):
        self.ratings = self.load_concreteness_ratings()

    def load_concreteness_ratings(self) -> Dict[str, float]:
        f = open(CSV_LOCATION)
        f.readline() # skip column titles
        concreteness_ratings = {}
        for line in f:
            data = line.split("\t")
            concreteness_ratings[data[0]] = float(data[2])
        
        return concreteness_ratings
        
    def get_rating(self, word: str) -> float:
        if word in self.ratings:
            print("concreteness: " + str(self.ratings[word]))
            return self.ratings[word]

        return 5.0 # it's out of 5, let's just assume it is concrete enough if we can't find it

    def is_concrete_enough(self, word: str) -> bool:
        if self.get_rating(word) >= 2.5: # shrug
            return True
        
        return False