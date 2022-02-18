import argparse
import string

from typing import List, Set


WORD_SIZE = 5
MAX_WORDS = 30


def solve(tries: List[str], colours: List[str], wordlist: List[str]):
    """
    Return most suitable words for the Wordle based on the information given.

    Args:
        tries (List[str]):
            The words already tried. Can be an empty list.
        colours (List[str]):
            The colours corresponding to the words already tried.
        wordlist (List[str]):
            A list containing all valid words.

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
    wordlist = filter(lambda w: is_valid(w, possible_chars, seen_chars), wordlist)
    wordlist = sorted(wordlist, key=score_word)

    return wordlist


def is_valid(word: str, possible_chars: List[Set[str]], seen_chars: Set[str]):
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


def score_word(word: str):
    """
    Score a word
    """

    return 0


if __name__ == "__main__":
    # Parse arguments
    cli = argparse.ArgumentParser()
    cli.add_argument(
        "--words",
        nargs="*",
        type=str,
        default=[],
    )
    cli.add_argument(
        "--colours",
        nargs="*",
        type=str,
        default=[],
    )

    args = cli.parse_args()

    tries = args.words
    colours = args.colours

    # Load WordList
    wordlist = []
    with open("wordlist.txt") as f:
        wordlist = f.read().split()

    # Return top N
    print(solve(tries, colours, wordlist)[:MAX_WORDS])
