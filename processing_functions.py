import pandas as pd
import numpy as np
from collections import Counter

def count_words(text):
    counts = Counter()
    for word in text:
        counts.update(word)
    return counts
