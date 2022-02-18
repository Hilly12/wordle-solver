import argparse
import numpy as np
import string

from typing import List, Set, Dict


WORD_SIZE = 5


def solve(
    tries: List[str],
    colours: List[str],
    wordlist: List[str],
    entropies: Dict[str, float]
) -> List[str]:
    """
    Return most suitable words for the Wordle based on the information given.

    Args:
        tries (List[str]):
            The words already tried. Can be an empty list.
        colours (List[str]):
            The colours corresponding to the words already tried.
        wordlist (List[str]):
            A list containing all valid words.
        entropies (Dict[str, float]):
            A dictionary mapping from words to their entropies.

    Returns:
        List[str]:
            A list containing the recommended words in order.
    """

    # Initialize possible chars to all characters in the alphabet
    possible_chars = [set([ch for ch in string.ascii_lowercase]) for i in range(WORD_SIZE)]

    # Initialize set of chars seen that the word must have
    seen_chars = set()

    # Prune possible chars based on information
    for word, word_cols in zip(tries, colours):
        for i, (ch, col) in enumerate(list(zip(word, word_cols))):

            if col == "g":
                possible_chars[i] = set([ch])
                seen_chars.add(ch)

            elif col == "y":
                possible_chars[i].discard(ch)
                seen_chars.add(ch)

            else:
                for i in range(WORD_SIZE):
                    possible_chars[i].discard(ch) 

    # Filter out invalid words and sort the remaining by their scores
    wordlist = list(filter(lambda w: is_valid(w, possible_chars, seen_chars), wordlist))
    wordlist = sorted(wordlist, key=lambda w: entropies[w], reverse=True)

    return wordlist


def is_valid(word: str, possible_chars: List[Set[str]], seen_chars: Set[str]) -> bool:
    """
    Check if a word is valid.
    """

    for i, ch in enumerate(word):
        if ch not in possible_chars[i]:
            return False

    word_chars = set(word)
    for ch in seen_chars:
        if ch not in word_chars:
            return False

    return True


def compute_entropies(wordlist: List[str]) -> Dict[str, float]:
    """
    Compute the entropies of all words in the wordlist.

    Args:
        wordlist (List[str]):
            A list containing all valid words.

    Returns:
        Dict[str, float]:
            A dictionary mapping from words to their entropies.
    """

    # Create a matrix consisting of each word encoded as a vector of ascii numbers
    # and all of its rotations.
    word_matrix = np.zeros((len(wordlist), WORD_SIZE, WORD_SIZE), dtype=np.int64)
    for i in range(len(wordlist)):
        for j in range(WORD_SIZE):
            for k in range(WORD_SIZE):
                word_matrix[i, j, k] = ord(wordlist[i][(k + j) % WORD_SIZE])

    # Compute the entropy of a word using the probability that the tiles are a
    # certain colour given the word has been chosen.
    entropies = dict()
    for i in range(len(wordlist)):
        equal = (word_matrix == word_matrix[i, 0, :]).astype(np.int64)
        equal[:, 0, :] *= 2
        hashes = (equal.max(axis=1) * (np.arange(1, WORD_SIZE + 1) * 4)).sum(axis=1)
        probs = np.unique(hashes, return_counts=True)[1] / len(wordlist)
        entropy = -np.sum(probs * np.log2(probs))
        entropies[wordlist[i]] = entropy

    return entropies


if __name__ == "__main__":
    # Parse arguments
    cli = argparse.ArgumentParser(description="Solve the daily wordle.")
    cli.add_argument(
        "-w",
        "--words",
        nargs="*",
        type=str,
        default=[],
        help="The words already tried in lowercase i.e. stare"
    )
    cli.add_argument(
        "-c",
        "--colours",
        nargs="*",
        type=str,
        default=[],
        help="The colours assigned to the word by the wordle in the form i.e. gg*y*"
    )
    cli.add_argument(
        "-m",
        "--max_words",
        type=int,
        default=50,
        help="The maximum number of words to show"
    )

    args = cli.parse_args()

    tries = args.words
    colours = args.colours
    max_words = args.max_words
    
    print("=============")
    print("Wordle Solver")
    print("=============")
    print()


    # Load word list
    wordlist = []
    with open("wordlist.txt") as f:
        wordlist = f.read().split()


    # Compute entropies
    print("Calculating entropies...")
    entropies = compute_entropies(wordlist)
    print("Done.")
    print()
    

    if len(tries) == 0 or len(tries) == 0:
        # Interactive mode
        tries = []
        colours = []

        top_words = solve(tries, colours, wordlist, entropies)
        print("Top starting words")
        print("------------------")
        print(", ".join(top_words[:max_words]))

        while len(top_words) > 1:
            print()

            try:
                word = input("Enter the word you tried: ")
                tries.append(word.lower()[:WORD_SIZE])

                cols = input("Enter the wordle colours: ")
                colours.append(cols.lower()[:WORD_SIZE])

            except KeyboardInterrupt:
                print()
                exit()
            
            top_words = solve(tries, colours, wordlist, entropies)
            print()
            print("Top words for this try")
            print("----------------------")
            print(", ".join(top_words[:max_words]))
            print()

        if len(top_words) == 1:
            print("Found match.")
    
        else:
            print("Unable to find match.")

    else:
        # Direct usage
        print()
        print("Top words")
        print("---------")
        print(", ".join(solve(tries, colours, wordlist, entropies)[:max_words]))
        print()
