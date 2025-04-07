import pandas as pd
from collections import Counter
import ast
import string
import re

def convert_to_list(data:str, cut_lead:int=0, cut_tail:int=0) -> list:
    """
    Converts a string representation of a list into an actual Python list.

    Args:
        data (str): A string that resembles a Python list (e.g., "[1, 2, 'a']").
        cut_lead (int, optional): The number of characters to remove from the beginning of the string. Defaults to 0.
        cut_tail (int, optional): The number of characters to remove from the end of the string. Defaults to 0.

    Returns:
        list: The converted Python list. Returns an empty list if the input string cannot be parsed.

    Example:
        >>> convert_to_list("[1, 2, 'a']")
        [1, 2, 'a']

        >>> convert_to_list("some invalid string")
        []

        >>> convert_to_list("[1, 2, 3, 4, 5]", cut_lead=1, cut_tail=-1)
        [2, 3, 4]
    """
    if cut_tail == 0:
        cut_tail = len(data)
    data = data[cut_lead:cut_tail]
    try:
        actual_list = ast.literal_eval(data)
    except Exception as e:
        actual_list = []
        print(e)

    return list(actual_list)

def remove_stop_words(ingredients: list[str], stop_words: set[str]) -> list[str]:
    """
    Removes common words and punctuation from a list of ingredient strings.

    Args:
        ingredients (list[str]): A list of strings, where each string represents an ingredient.
        stop_words (set[str]): A set of common words to be removed.

    Returns:
        list[str]: A list of strings, with common words and punctuation removed from each ingredient.

    Example:
        >>> ingredients = ["1 cup of flour, sifted", "2 eggs and milk"]
        >>> stop_words = {"of", "and"}
        >>> remove_common_words(ingredients, stop_words)
        ['cup flour sifted', 'eggs milk']
    """
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

def remove_nans_from_list(input_list: list[str]) -> list:
    """
    Removes NaN or None values from a list.

    Args:
        input_list (list): The list to process.

    Returns:
        list: The list with NaN or None values removed. Returns an empty list if the input is not a list.

    Example:
        >>> remove_nans_from_list([1, None, 'a', float('nan'), 3.0])
        [1, 'a', 3.0]

        >>> remove_nans_from_list('not a list')
        []
    """
    if isinstance(input_list, list): #handles nan/none values.
        return [item for item in input_list if pd.notna(item)]
    else:
        return []

def counting(data_list, to_count=""):
    """
    Counts the occurrences of strings within a list of lists, optionally filtering by a suffix.

    Args:
        data_list (list[list[str]]): A list of lists, where each inner list contains strings.
        to_count (str, optional): An optional string suffix. If provided, only strings ending with this suffix are counted. Defaults to "".

    Returns:
        Counter: A Counter object containing the counts of the strings that match the criteria.

    Example:
        >>> data = [["apple", "banana", "orange_pie"], ["grape", "apple_pie", "kiwi"]]
        >>> counting(data, "_pie")
        Counter({'orange_pie': 1, 'apple_pie': 1})

        >>> counting(data)
        Counter({'apple': 1, 'banana': 1, 'orange_pie': 1, 'grape': 1, 'apple_pie': 1, 'kiwi': 1})
    """
    counts = Counter()
    for small_list in data_list:
        for item in small_list:
            if item.endswith(to_count):
                counts[item] += 1

    return counts

def remove_list_items(data_list, items_to_drop):
    """
    Removes specified items from a given list.

    Args:
        data_list (list): The list from which items will be removed.
        items_to_drop (list): A list of items to remove from data_list.

    Returns:
        list: A new list containing all items from data_list except those in items_to_drop.

    Example:
        >>> remove_list_items([1, 2, 3, 4, 5], [2, 4])
        [1, 3, 5]

        >>> remove_list_items(['apple', 'banana', 'cherry', 'date'], ['banana', 'date', 'grape'])
        ['apple', 'cherry']
    """
    modified_list = []
    for item in data_list:
        if item not in items_to_drop:
            modified_list.append(item)
    return modified_list

def remove_plural_s(ingredients:list, letters_to_replace:str, replace_with:str):
    """
    Removes or replaces trailing letters from a list of ingredient strings, primarily handling plural 's' removal.

    Args:
        ingredients (list[str]): A list of ingredient strings.
        letters_to_replace (str): The trailing letters to remove or replace. If 's', handles plural 's' removal with exceptions.
        replace_with (str): The string to replace the trailing letters with (if not removing 's').

    Returns:
        list[str]: A list of modified ingredient strings.

    Example:
        >>> remove_plural_s(['apples', 'bananas', 'carrots', 'bus'], 's', '')
        ['apple', 'banana', 'carrots', 'bus']

        >>> remove_plural_s(['boxes', 'foxes', 'dishes', 'cats'], 'es', '')
        ['box', 'fox', 'dish', 'cats']

        >>> remove_plural_s(['boxes', 'foxes', 'dishes', 'cats'], 'es', 'e')
        ['boxe', 'foxe', 'dishe', 'cats']
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

def remove_words(ingredient_list:list, words_to_remove:set) -> list:
    """
    Removes specified words from ingredient strings within a list.

    Args:
        ingredient_list (list[str]): A list of ingredient strings.
        words_to_remove (set[str]): A set of words to remove (case-insensitive).

    Returns:
        list[str]: A new list with modified ingredient strings, with empty strings removed.

    Example:
        >>> remove_words(['1 cup of flour', '2 large eggs and milk'], {'of', 'and'})
        ['1 cup flour', '2 large eggs milk']

        >>> remove_words(['salt and pepper', 'a pinch of sugar'], {'salt', 'a'})
        ['pepper', 'pinch of sugar']

        >>> remove_words(['', 'remove all these words', ''], {'remove', 'all', 'these', 'words'})
        [''] # Demonstrates removal of empty strings.
    """
    modified_list = []
    for ingredient in ingredient_list:
        words = ingredient.split()  # Split into words
        filtered_words = [word for word in words if word.lower() not in words_to_remove]
        modified_ingredient = " ".join(filtered_words)  # Reconstruct the string
        modified_list.append(modified_ingredient)
        modified_list = [item for item in modified_list if item !=""]
    return modified_list