APPROXIMATE_REGEX = r'(?i)(circa|around|about|(?<!d)ca?\.|\[ca]|^ca |ca$)'
UNCERTAIN_REGEX = r"(?i)((proba|possi)ba?ly|\?)"
PREPOSITION_REGEX = r"(?i)^(?:sometimes )?(up to|in|on|by)( the)? "
AD_REGEX = r"( A.?D.?|CE$|CE-)"
CENTURY_VARIATION = "(?i)centuries"
CENTURY_STANDARD = "century"
ORDINALS = "st|nd|rd|th"
SEPARATORS = ['to', 'and', 'or']
BETWEEN = "between"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december", "spring", "summer", "fall|autumn", "winter"]
PART_OF_DAY = ["sunrise", "(^| )day", "morning", "afternoon", "sunset", "evening", "night"]
DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SEASON = "session|season"
