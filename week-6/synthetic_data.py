# from llama_index.llms.ollama import Ollama
# import dspy
import csv
import random
import re

# llm = Ollama(model="llama3", request_timeout=60.0)

# you can use DSPY (https://github.com/stanfordnlp/dspy), but you can also choose another method of interacting with an LLM
# dspy.settings.configure(lm=llm)

# Task: implement a method, that will take a query string as input and produce N misspelling variants of the query.
# These variants with typos will be used to test a search engine quality.
# Example
# Query: machine learning applications
# Possible Misspellings:
# "machin learning applications" (missing "e" in "machine")
# "mashine learning applications" (phonetically similar spelling of "machine")
# "machine lerning aplications" (missing "a" in "learning" and "p" in "applications")
# "machin lerning aplications" (combining multiple typos)
# "mahcine learing aplication" (transposed letters in "machine" and typos in "learning" and "applications")
#
# Questions:
# 1. Does the search engine produce the same results for all the variants?
# 2. Do all variants make sense?
# 3. How to improve robustness of the method, for example, skip known abbreviations, like JFK or NBC.
# 4. Can you test multiple LLMs and figure out which one is the best?
# 5. Do the misspellings capture a variety of error types (phonetic, omission, transposition, repetition)?


def replacement(word):
    """This function creates typos in words based on a qwerty keyboard"""
    asdfghjkl_list = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
    new_word = []
    replaced = False

    for letter in word:
        if not replaced and letter in asdfghjkl_list and letter != "l":
            idx = asdfghjkl_list.index(letter)
            new_word.append(asdfghjkl_list[idx + 1])
            replaced = True
        else:
            new_word.append(letter)

    return "".join(new_word)

def omission(word):
    '''This function removes a random letter from a word'''
    if len(word) < 2:
        return word
    pos = random.randint(1, len(word) - 1)
    return word[:pos] + word[pos + 1:]


def transposition(word):
    '''This function transposes letters in a word'''
    if len(word) <= 2:
        return word
    pos = random.randint(0, len(word) - 2)
    chars = list(word)
    chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    return "".join(chars)

def doubling(word):
    '''This function doubles letters in a word'''
    if len(word) < 1:
        return word
    pos = random.randint(1, len(word) - 1) #do not double first letter
    return word[:pos] + word[pos] + word[pos:]


def combine_typos(query, n=2):
    """This function combines typos"""
    words = query.split()
    variants = []

    for x in range(n):
        new_words = []
        for word in words:
            if random.randint(0, 10) <= 3:
                typo_function = random.choice(
                    [
                        replacement,
                        omission,
                        transposition,
                        doubling,
                    ]
                )
                new_word = typo_function(word)
                new_words.append(new_word)
            else:
                new_words.append(word)
        variants.append(" ".join(new_words))
    return variants


def main():
    '''
    This function reads a csv with queries,
    adds typos to the queries
    and prints the output to a different csv
    '''

    input_csv = "web_search_queries.csv"
    output_csv = "web_search_queries_typos.csv"
    nr_variants = 3
    
    with open(input_csv, "r", encoding="utf-8") as f_in, \
         open(output_csv, "w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = ["Original Query"] + [f"Variant {i+1}" for i in range(nr_variants)]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            query = row["Query"]
            variants = combine_typos(query, n=nr_variants)
            row_data = {"Original Query": query}
            for i, variant in enumerate(variants):
                row_data[f"Variant {i+1}"] = variant
            writer.writerow(row_data)


if __name__ == "__main__":
    main()