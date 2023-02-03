APPROXIMATE_REGEX = r'(?i)(približno)'
UNCERTAIN_REGEX = r"(?i)(morda|\?)"
PREPOSITION_REGEX = r"(?i)^(do|in|na|po|leta) "
AD_REGEX = r"( A.?D.?|n. št)"
CENTURY_VARIATION = "(?i)stoletj[ea]"
CENTURY_STANDARD = "stoletje"
ORDINALS = "\\."
SEPARATORS = ['in']
BETWEEN = "med"
MONTHS = ["januar", "februar", "marec", "april", "maj", "junij", "julij", "avgust", "september", "oktober", "november",
          "december", "pomlad", "poletje", "jesen", "zima"]
PART_OF_DAY = ["sončni vzhod", "dan", "jutro", "popoldne", "sončni zahod", "večer", "noč"]
DAYS_OF_WEEK = ["ponedeljek", "torek", "sreda", "četrtek", "petek", "sobota", "nedelja"]
SEASON = "sezona"
CENTURY_PART = "(?i)((?:fir|1)st|(?:2|seco)nd|(?:3|thi)rd|fourth|last) (quarter|half|third),?(?: of(?: the)?)?"
