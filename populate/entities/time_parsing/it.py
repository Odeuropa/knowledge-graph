APPROXIMATE_REGEX = r'(?i)(circa|(?<!d)ca?\.|\[ca]|^ca |ca$)'
UNCERTAIN_REGEX = r"(?i)(forse|\?)"
PREPOSITION_REGEX = r"(?i)^il "
AD_REGEX = r"dC\.?$"
CENTURY_VARIATION = r"(?i)(sec\.|se? (?=[XVI]+))"
CENTURY_STANDARD = "secolo"
ORDINALS = "o|a"
SEPARATORS = ['e', 'al?', 'o']
BETWEEN = "tra"
MONTHS = ["gennaio", "febbra[ji]o", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
          "novembre", "dicembre", "primavera", "estate", "autunno", "inverno"]
PART_OF_DAY = ["alba", "giorno|dí|diurn.", "mattina", "pomeriggio", "tramonto", "sera", "notte"]
DAYS_OF_WEEK = ["luned[ií]", "marted[ií]", "mercoled[ií]", "gioved[ií]", "venerd[ií]", "sabato", "domenica"]
SEASON = "stagione"
