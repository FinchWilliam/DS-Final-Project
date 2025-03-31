import pandas as pd
import numpy as np
from collections import Counter
import ast
import string
import re

def convert_to_list(data, letters_to_cut=0):
    """
    Takes a string that looks like a list and converts it into an actual list

    Args:
        data(string): listlike string to be converted into a list
    
    Returns:
        actual_list(list) as a list

    """
    data = data[letters_to_cut:]
    try:
        actual_list = ast.literal_eval(data)
    except Exception as e:
        actual_list = []
        print(e)

    return list(actual_list)

def remove_common_words(ingredients, stop_words):
     complete_list = []
     translator = str.maketrans('','',string.punctuation)
     for ingredient in ingredients:
          new_list = []
          words = ingredient.split()
          for word in words:
               word = word.translate(translator)
               word = re.sub(r'\d+','',word)
               word = word.strip()
               if word not in stop_words:            
                    new_list.append(word)
          complete_list.append(" ".join(new_list).strip())
     return complete_list

def remove_nans_from_list(input_list):
    """
    Removes NaN values from a list.

    Args:
        input_list (list): The list to process.

    Returns:
        list: The list with NaN values removed.
    """
    if isinstance(input_list, list): #handles nan/none values.
        return [item for item in input_list if pd.notna(item)]
    else:
        return []
    
    
def counting(data_list, to_count=""):
    counts = Counter()
    for small_list in data_list:
        for item in small_list:
            if item.endswith(to_count):
                counts[item] += 1

    return counts

def remove_list_items(data_list, items_to_drop):
    modified_list = []
    for item in data_list:
        if item not in items_to_drop:
            modified_list.append(item)
    return modified_list

def remove_plural_s(ingredients, letters_to_replace, replace_with):
    """
    Removes the trailing 's' from a word, handling exceptions.

    Args:
        ingredient: The ingredient string.

    Returns:
        The modified ingredient string.
    """
    list_ingredients = []
    for ingredient in ingredients:
        ingredient = ingredient.lower()
        if letters_to_replace.lower() == "s":
            if ingredient.lower().endswith(letters_to_replace):
                if len(ingredient) > 1 and ingredient[-2] not in ["a", "e", "i", "o", "u", "s"]:
                    list_ingredients.append(ingredient[:-1])
                else:
                    list_ingredients.append(ingredient)
            else:
                list_ingredients.append(ingredient)
        else:
            if len(ingredient) > len(letters_to_replace) and ingredient.endswith(letters_to_replace):
                list_ingredients.append(ingredient[:-len(letters_to_replace)] + replace_with)
            else:
                list_ingredients.append(ingredient)
    return list_ingredients

def counting(data_list, to_count):
    counts = Counter()
    for small_list in data_list:
        for item in small_list:
            if item.endswith(to_count):
                counts[item] += 1

    return counts

def remove_words(ingredient_list, words_to_remove):
    """
    Removes specified words from ingredient strings within a list.

    Args:
        ingredient_list: A list of ingredient strings.
        words_to_remove: A set of words to remove (case-insensitive).

    Returns:
        A new list with modified ingredient strings.
    """
    modified_list = []
    for ingredient in ingredient_list:
        words = ingredient.split()  # Split into words
        filtered_words = [word for word in words if word.lower() not in words_to_remove]
        modified_ingredient = " ".join(filtered_words)  # Reconstruct the string
        modified_list.append(modified_ingredient)
        modified_list = [item for item in modified_list if item !=""]
    return modified_list