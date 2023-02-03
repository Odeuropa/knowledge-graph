APPROXIMATE_REGEX = r'(?i)(circa|(?<!d)ca?\.|\[ca]|^ca |ca$)'
UNCERTAIN_REGEX = r"(?i)(posiblemente|\?|¿)",
PREPOSITION_REGEX = r"(?i)^ "  # nothing to say
AD_REGEX = r"( A.?D.?|CE$|CE-)"
CENTURY_VARIATION = r"(?i)(soglo|s(ig)?\. ?)"
CENTURY_STANDARD = "siglo"
SEPARATORS = ['y']
BETWEEN = "entre"
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
          "noviembre", "diciembre", "primavera", "verano", "otoño", "invierno"]
CENTURY_PART = "(?i)([1234][]|pr?i[mn]era?|segund[oa]|segon|tercer|UUUltimo?) (cuarto|quart|mitad|meitat|tercio|1/3)(?: del)?";
