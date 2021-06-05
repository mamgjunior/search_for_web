def search4vowels(phrase: str) -> set:
    """Return any vowels found in a supplied word."""
    vowels = set('aeiou')
    return vowels.intersection(set(phrase))


def search_for_letters(phrase: str, letters: str = 'aeiou') -> set:
    """Return a set of 'letters' found in 'phrase'."""
    return set(letters).intersection(set(phrase))
