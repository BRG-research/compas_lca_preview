import re

def sanitize_filename(name):
    """
    Replace illegal filename characters with "-", preserving unicode like umlauts.
    """
    if not name:
        return "UnnamedElement"

    # Replace any character that is not a unicode letter/number/underscore/hyphen/space
    # Keep characters like ä, ö, ü, ß, etc.
    # Allow space for readability, will replace with "-" after
    cleaned = re.sub(r'[^\w\säöüÄÖÜß-]', '-', name, flags=re.UNICODE)
    return cleaned.replace(" ", "-")