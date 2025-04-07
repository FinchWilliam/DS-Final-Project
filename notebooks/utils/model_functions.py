import re
import numpy as np
import pandas as pd

def levenshtein_distance(s1:str, s2:str) -> int:
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
    return closest_word

def recommend_items(sim_matrix, near_items, far_items, top_n=5):
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
    
    near_items = [item.lstrip().rstrip() for item in near_items.lower().split(',')]

    item_list = list(sim_matrix.columns) # create a list of all the items
    cleaned_near_items, near_error_codes = _clean_and_validate_items(items=near_items, item_list=item_list)
    if far_items:
        far_items = [item.lstrip().rstrip() for item in far_items.lower().split(',')]
        cleaned_far_items, far_error_codes = _clean_and_validate_items(items=far_items, item_list=item_list)
    else:
        cleaned_far_items = []
        far_error_codes = []
    error_codes = near_error_codes + far_error_codes #combine error codes for later use

    all_items = cleaned_far_items + cleaned_near_items # combine item lists for later use

    #calculate similarity for close items
    near_similarity_scores_list = [sim_matrix[item].drop(cleaned_near_items, errors='ignore') for item in cleaned_near_items]
    combined_near_similarity_scores = pd.concat(near_similarity_scores_list, axis=1).min(axis=1)
    combined_near_similarity_scores = combined_near_similarity_scores.sort_values(ascending=False)

    #calculate dissimilarity for far items
    far_similarity_scores_list = [sim_matrix[item].drop(cleaned_far_items, errors='ignore') for item in cleaned_far_items]
    if far_similarity_scores_list:
        combined_far_similarity_scores = pd.concat(far_similarity_scores_list, axis=1).max(axis=1)
    else:
        combined_far_similarity_scores = pd.Series(index=combined_near_similarity_scores.index, data=0)
    
    combined_similarity_scores = combined_near_similarity_scores - combined_far_similarity_scores
    combined_similarity_scores = combined_similarity_scores.drop(all_items, errors='ignore')
    combined_similarity_scores = combined_similarity_scores.sort_values(ascending = False)

    return combined_similarity_scores.head(top_n), error_codes

def _clean_and_validate_items(items: list[str], item_list: list[str]) -> tuple[list[str], list[str]]:
    """Cleans item names, validates their existence, and finds closest matches if needed."""
    cleaned_items = []
    error_codes = []
    for item in items:
        cleaned_item = re.sub(r'[^a-zA-Z0-9 ]', '', item)
        if cleaned_item not in item_list:
            cleaned_item = find_closest_word(item, item_list)
            error_codes.append(f"Ingredient {item} not in our recommender yet, returning closest '{cleaned_item}'")
        cleaned_items.append(cleaned_item)
    return cleaned_items, error_codes

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
    Calculates the cosine similarity matrix from a co-occurrence matrix.

    Args:
        co_matrix (pd.DataFrame): The co-occurrence matrix, where rows and columns
            represent items, and values represent the frequency with which items
            co-occur.

    Returns:
        pd.DataFrame: The cosine similarity matrix. The values represent the
            cosine similarity between items. The index and columns match those of
            the input `co_matrix`.
    """
    n_items = co_matrix.shape[0]
    similarity_matrix = pd.DataFrame(index = co_matrix.index, columns = co_matrix.index)
    for i in range(n_items):
        for j in range(n_items):
            similarity_matrix.iloc[i,j] = cosine_similarity(co_matrix.iloc[i], co_matrix.iloc[j])
    return similarity_matrix

def recommend_ingredients_pairwise(ingredient, pair_counts, top_n:int =5) -> list:
    """
    Recommends ingredients that pair well with a given ingredient based on co-occurrence counts.

    Args:
        ingredient (str): The ingredient for which to find recommendations.
        pair_counts (dict): A dictionary where keys are tuples of ingredient pairs
            (e.g., ("apple", "cinnamon")) and values are the number of times they
            co-occur.
        top_n (int, optional): The maximum number of recommendations to return.
            Defaults to 5.

    Returns:
        list: A list of the top `top_n` recommended ingredients (strings), sorted
            by co-occurrence count in descending order.  Returns an empty list
            if no co-occurring ingredients are found.
    """
    recommendations = []
    for pair, count in pair_counts.items():
        if ingredient in pair:
            other_ingredient = pair[0] if pair[1] == ingredient else pair[1]
            recommendations.append((other_ingredient, count))
    recommendations.sort(key = lambda x: x[1], reverse = True)
    return [item[0] for item in recommendations[:top_n]]

