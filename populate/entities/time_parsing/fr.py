APPROXIMATE_REGEX = r'(?i)(circa|vers |(?<!d)ca?\.|\[ca]|^ca |ca$)'
UNCERTAIN_REGEX = r"(?i)\?"
PREPOSITION_REGEX = r"(?i)^le "
AD_REGEX = r"( A.?D.?|CE$|CE-)"
CENTURY_VARIATION = "(?i)si[èeé]cles"
CENTURY_STANDARD = "siècle"
ORDINALS = "eme|e"
SEPARATORS = ['et', 'à', 'au']
BETWEEN = "entre"
MONTHS = ["janvier", "fevrier", "mars", "avril", "mai",  "juin", "juillet", "ao[uû]t", "septembre", "octobre", "novembre",
          "d[eéè]cembre", "printemps", "été", "automne", "hiver"]
PART_OF_DAY = ["aube", "jour", "matin(ée)?", "après-midi", "coucher de soleil", "soir(ée)?", "nuit"]
DAYS_OF_WEEK = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
SEASON = "saison"
