APPROXIMATE_REGEX = r'(?i)(\Wum |ca?\.|\[ca]|^(?:ca|um) |ca$)'
UNCERTAIN_REGEX = r"(?i)(vielleicht|\?)"
PREPOSITION_REGEX = r"(?i)^(bis zu|im|auf|von) "
AD_REGEX = r"( A.?D.?|CE$|CE-|n. Chr.?)"
CENTURY_VARIATION = "(?i)(jahrhunderts?|jh.)"
CENTURY_STANDARD = "jahrhundert"
ORDINALS = " ?\\."
SEPARATORS = ['und']
BETWEEN = "zwischen"
MONTHS = ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november",
          "dezember", "frühling", "sommer", "herbst", "winter"]
PART_OF_DAY = ["sonnenaufgang", "tag", "morgen", "nachmittag", "sonnenuntergang", "abend", "nacht"]
DAYS_OF_WEEK = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]
SEASON = "(?i)(spätestens|saison|datierung(?: engl)?:?|aufnahme(?:zeitraum)?:?)"
CENTURY_PART = "(?i)((?:fir|1)st|(?:2|seco)nd|(?:3|thi)rd|fourth|last) (quarter|half|third),?(?: of(?: the)?)?"
