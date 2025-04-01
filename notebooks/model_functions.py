import re
import numpy as np
import pandas as pd

def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance between two strings.
    This is a measure of the number of single-character edits
    (insertions, deletions, or substitutions) required to change one
    string into the other.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between the two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)    # Ensure s1 is the longer string.

    # If s1 is empty, the distance is just the length of s2
    if len(s1) == 0:
        return len(s2)

    # Create a distance matrix (v0 is the previous row, v1 is the current row)
    v0 = [i for i in range(len(s2) + 1)]
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        # Calculate the current row (v1)
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1,                 # Deletion
                            v0[j + 1] + 1,             # Insertion
                            v0[j] + cost)              # Substitution
        v0 = v1[:]  # Copy the current row to the previous row

    return v1[len(s2)]  # The last cell of the matrix is the Levenshtein distance
    
def find_closest_word(input_word, word_list=None):
    """
    Finds the closest word in a given list to the input word.
    Closeness is determined by the Levenshtein distance (edit distance).

    Args:
        input_word (str): The word to find the closest match for.
        word_list (list, optional): A list of words to search within.
            If None. Defaults to None.

    Returns:
        str: The closest word from the list, or None if the list is empty.
    """

    if not word_list:
        return None  # Return None if the word list is empty

    # Preprocess the input word: Remove non-alphanumeric characters and lowercase
    input_word = re.sub(r'[^a-zA-Z0-9]', '', input_word).lower()

    closest_word = None
    min_distance = float('inf')  # Initialize with infinity

    for word in word_list:
        # Preprocess each word in the list: Remove non-alphanumeric characters and lowercase
        test_word = re.sub(r'[^a-zA-Z0-9]', '', word).lower()
        distance = levenshtein_distance(input_word, test_word)  # Use the helper function

        if distance < min_distance:
            min_distance = distance
            closest_word = word
    # print(min_distance)
    return closest_word

def recommend_items(sim_matrix, item_names, top_n=5):
    """
    Recommends the top_n most similar items based on cosine similarity.

    Args:
        co_matrix_pd (pd.DataFrame): The co-occurrence matrix as a Pandas DataFrame.
        item_name (str): The name of the item for which to find recommendations.
        top_n (int, optional): The number of top recommendations to return. Defaults to 5.

    Returns:
        pd.Series: A Pandas Series containing the top_n most similar items and their similarity scores,
                  sorted in descending order of similarity.  Returns an empty series if the item_name is not found.
    """
    item_names = item_names.split(',')
    item_names = [item.lstrip().rstrip() for item in item_names]

    cleaned_items = []
    error_codes = []
    item_list = list(sim_matrix.columns) # create a list of all the items
    for item_name in item_names: # clean every item in the list
        item_name = item_name.lower() #remove capitilazation
        item_test = re.sub(r'[^a-zA-Z0-9 ]', '', item_name) #remove punctuation
        if item_test not in item_list: #check if our item is in the dataset, if not return the closest result
            # print(f"Item '{item_name}' not in our dataset")
            item_test = find_closest_word(item_name, item_list)
            # print(f"Selected Closest word in list: {item_name}")
            error_codes.append(f"Ingredient {item_name} not in our recommender yet, returning closest '{item_test}'")
        cleaned_items.append(item_test)

    similarity_scores_list = [sim_matrix[item].drop(cleaned_items, errors='ignore')for item in cleaned_items]
    combined_similarity_scores = pd.concat(similarity_scores_list, axis=1).min(axis=1)
    combined_similarity_scores = combined_similarity_scores.sort_values(ascending=False)

    return combined_similarity_scores.head(top_n), error_codes

def cosine_similarity(vec1, vec2):
    """
    Calculates the cosine similarity between two vectors.

    Args:
        vec1 (numpy.ndarray): The first vector.
        vec2 (numpy.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    if np.all(vec1==0) or np.all(vec2==0):
        return 0.0 #handle zero vectors for division by zero avoidance
    
    dot_product = np.dot(vec1, vec2)
    magnitude_vec1 = np.linalg.norm(vec1)
    magnitude_vec2 = np.linalg.norm(vec2)
    return dot_product / (magnitude_vec1 * magnitude_vec2)

def calculate_similarity_matrix(co_matrix):
    """
    Calculates the cosine similarity matrix from a co-occurrence matrix, given as a Pandas DataFrame.

    Args:
        co_matrix_pd (pd.DataFrame): The co-occurrence matrix as a Pandas DataFrame.

    Returns:
        pd.DataFrame: The cosine similarity matrix, as a Pandas DataFrame.
    """
    n_items = co_matrix.shape[0]
    similarity_matrix = pd.DataFrame(index = co_matrix.index, columns = co_matrix.index)
    for i in range(n_items):
        for j in range(n_items):
            similarity_matrix.iloc[i,j] = cosine_similarity(co_matrix.iloc[i], co_matrix.iloc[j])
    return similarity_matrix

def recommend_ingredients_pairwise(ingredient, pair_counts, top_n=5):
    recommendations = []
    for pair, count in pair_counts.items():
        if ingredient in pair:
            other_ingredient = pair[0] if pair[1] == ingredient else pair[1]
            recommendations.append((other_ingredient, count))
    recommendations.sort(key = lambda x: x[1], reverse = True)
    return [item[0] for item in recommendations[:top_n]]

