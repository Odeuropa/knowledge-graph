APPROXIMATE_REGEX = r'(?i)(ongeveer)'
UNCERTAIN_REGEX = r"(?i)(misschien)"
PREPOSITION_REGEX = r"(?i)^(tot|in|op|door)? ?(den?|het|een)? "
AD_REGEX = r"( A.?D.?|CE$|CE-)"
CENTURY_VARIATION = r"(?i)(eeuw)"
CENTURY_STANDARD = "eeuw"
ORDINALS = "-?(?:e|ste|de|o| \\.)"
SEPARATORS = ['en']
BETWEEN = "tussen"
MONTHS = ["januari", "februari ", "maart ", "april", "mei ", "juni ", "juli", "augustus", "september ", "oktober ",
          "november", "december", "lente", "zomer", "herfst", "winter"]
PART_OF_DAY = ["zonsopgang", "dag", "ochtend|morgen", "middag", "zonsondergang", "avon[dt]", "nacht"]
DAYS_OF_WEEK = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
SEASON = "seizoen"
