import re
from rdflib import XSD
from datetime import datetime
import roman
from text_to_num import alpha2digit
from . import en, es, it, fr, nl, de, sl

ISO_DATE_FORMAT = "yyyy-MM-dd"
SLASH_LITTLE_ENDIAN = "%d/%m/%Y"

UCT_DATE_REGEX = r"\d{4}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[1-2]\d|3[0-1]))?)?(?:T(?:[0-1]\d|2[0-3]):[0-5]\d:[" \
                 "0-5]\dZ?)?"

CURLY_BRACKETS_REGEX = r"\(.*\)"
SQUARE_BRACKETS_REGEX = r"\[.*]"
ANY_BRACKETS_REGEX = r"[(\[\])]"

CIRCA_REGEX = r"(^ca | ca$)"
SINGLE_YEAR = r"^\d{3,4}s?$"

FULL_DATE_MULTI = r"(3[01]|[012]?[0-9]|\d{3,4})[-/ .](1[012]|0?\d)[-/ .](\d{2,4})"
MONTH_DATE_REGEX = r"(?:(\d{2})/(\d{4}))(?:-(\d{2})/(\d{4}))?"

langs = {
    'en': en,
    'es': es,
    'it': it,
    'fr': fr,
    'nl': nl,
    'de': de,
    'sl': sl
}


def date_format(dd, m, yy):
    if yy is None:
        yy = 'XXXX'
    elif len(yy) == 2:
        yy = "19" + yy

    # _type = XSD.gMonth
    formatted = yy + "-" + ("%02d" % int(m) if m != 0 else 'XX')
    if dd:
        # _type = XSD.date
        formatted += "-" + "%02d" % int(dd)

    return formatted  # , _type


def pad_year(year):
    y = str(year)
    prefix = ""
    if y.startswith("-"):
        prefix = "-"
        y = y.replace("-", "")

    y = prefix + y.zfill(4)
    return y


def decade2year(decade, end, modifier=0):
    # modifier: 0 = NONE, 1 = EARLY, 2 = LATE, 3 = MID
    if decade.endswith("0s"):
        decade = decade.zfill(5)
        if end:  # end decade
            end_digit = "9"
            if modifier == 1:
                end_digit = "4"
            if modifier == 3:
                end_digit = "8"
            return decade.replace("0s", end_digit)
        # start decade
        if modifier == 2:
            return decade.replace("0s", "5")
        if modifier == 3:
            return decade.replace("0s", "2")
        return decade.replace("s", "")

    # In cases like 1399s (`s` not preceded by 0)
    # I consider the `s` as an error and I strip it
    decade = decade.replace("s", "")

    # choice: mid-years (e.g. mid-1983) are not handle with month-precision
    return pad_year(decade)


def parse_edtf(edtf):
    parts = re.sub(r'[?%~]', '', edtf).split('/')
    if len(parts) == 1:  # single date
        start = end = parts[0]
    else:
        start, end = parts

    if start.startswith('X'):
        # uncertainty on the year, I can't transform into rdf date
        start = ''
    else:
        start = start.replace('XX', '01').replace('X', '1')
    if end.startswith('X'):
        # uncertainty on the year, I can't transform into rdf date
        end = ''
    else:
        end = end.replace('XX', '99').replace('X', '9')

    dashS = start.count('-')
    dashE = end.count('-')
    startType = XSD.date if dashS == 2 else XSD.gMonth if dashS == 1 else XSD.gYear
    endType = XSD.date if dashE == 2 else XSD.gMonth if dashE == 1 else XSD.gYear

    return start, end, startType, endType


def get_edtf_uncertain_sym(uncertain, approximate):
    # get edtf for a single date
    sym = ''
    if uncertain and approximate:
        sym = "%"
    elif uncertain:
        sym = "?"
    elif approximate:
        sym = "~"

    return sym


def get_edtf(date, uncertain=False, approximate=False):
    # get edtf for a single date
    if date is None:
        return ''

    return date, get_edtf_uncertain_sym(uncertain, approximate)


def compute_edtf(startDate, endDate, startUncertain, startApproximate, endUncertain, endApproximate, before_after):
    # get edtf for a time span
    if startDate is None and endDate is None:
        return '', ''

    start, start_sym = get_edtf(startDate, startUncertain, startApproximate)
    end, end_sym = get_edtf(endDate, endUncertain, endApproximate)

    # 0 = NONE, +1 = ON OR AFTER, +2 = AFTER, -1 = ON OR BEFORE, -2 = BEFORE
    af = '..' if before_after > 0 else ''
    bf = '..' if before_after < 0 else ''

    if startDate is not None:
        if start == end and start_sym == end_sym:
            return bf + start + af + start_sym
        elif endDate is not None:
            if before_after == 2:
                return end + end_sym + "/.."
            elif before_after == -2:
                return "../" + start + start_sym
            else:
                return bf + start + start_sym + "/" + end + af + end_sym
        else:
            return bf + start + af + start_sym + "/"
    else:
        return "/" + bf + end + af + end_sym


def detect_approximation(date, regex):
    matcher = re.search(regex, date)
    approximate = True if matcher else False
    if approximate:
        date = re.sub(regex, " ", date)
    return date, approximate


def month_to_num(month, localised_months):
    month = month.lower()
    mi = -1
    for i, m in enumerate(localised_months):
        if re.search(m, month):
            mi = i
            break
    mi += 1

    # 21     Spring (independent of location)
    # 22     Summer (independent of location)
    # 23     Autumn (independent of location)
    # 24     Winter (independent of location)
    if mi > 12:
        mi += 8
    return mi


def parse_matched_date(dd, mm, yy, localised_months):
    mi = month_to_num(mm, localised_months)
    return date_format(dd, mi, yy)


def pack_edtf_list(parsed, sym):
    if parsed[0] == parsed[-1]:
        return parsed[0] + sym
    return parsed[0] + sym + '/' + parsed[-1] + sym


def parse_date(date, lang='en'):
    if not date:
        return None
    if date == 's.d':
        return None

    lg = langs.get(lang, langs['en'])

    date = date.strip()
    date, uncertain = detect_approximation(date, lg.UNCERTAIN_REGEX)
    date, approximate = detect_approximation(date, lg.APPROXIMATE_REGEX)

    # preliminary parsing
    date = re.sub(lg.PREPOSITION_REGEX, "", date)  # in November
    date = re.sub(CURLY_BRACKETS_REGEX, "", date)  # curly brackets
    date = re.sub(SQUARE_BRACKETS_REGEX, "", date)  # square brackets
    date = re.sub(ANY_BRACKETS_REGEX, "", date)  # orphan brackets
    date = re.sub(lg.SEASON, "", date)  # unnecessary word

    date = re.sub("\"", "", date)
    date = date.strip()
    if not date:
        return None

    date = re.sub(lg.AD_REGEX, "", date)
    date, circa = detect_approximation(date, CIRCA_REGEX)
    approximate = approximate or circa
    sym = get_edtf_uncertain_sym(uncertain, approximate)

    date = re.sub(lg.CENTURY_VARIATION, lg.CENTURY_STANDARD, date)
    date = re.sub(r"[.,]$", "", date)  # trailing punctuation
    date = re.sub(r"\(?(dated?|active)\)?", "", date)

    date = re.sub(r'^(\d{1,2}(?:st|nd|rd|th))C$', r'\1 ' + lg.CENTURY_STANDARD, date)
    date = re.sub(r"\s+", " ", date)  # double space to one space

    date = date.strip()

    modifier = 0

    # // 0 = NONE, +1 = ON OR AFTER, +2 = AFTER, -1 = ON OR BEFORE, -2 = BEFORE
    # matcher = BEFORE_PATTERN.matcher(date);
    # if (matcher.find()) {
    #   before_after = matcher.group(1).contains("or ") ? -1 : -2;
    #   date = date.replaceAll(BEFORE_REGEX, "").trim();
    # }
    # matcher = AFTER_PATTERN.matcher(date);
    # if (matcher.find()) {
    #   before_after = matcher.group(1).contains("or ") ? 1 : 2;
    #   date = date.replaceAll(AFTER_REGEX, "").trim();
    # }
    #
    # if (date.matches(("\d+ " + BEFORE_CHRIST))) {
    #   date = "-" + padYear(date.replaceAll(BEFORE_CHRIST, "").trim());
    #   if (startYear == null) {
    #     startYear = startDate = date;
    #     startType = XSDDatatype.XSDgYear;
    #   }
    #   endYear = endDate = date;
    #   endType = XSDDatatype.XSDgYear;
    # }

    # int modifier = 0; // 0 = NONE, 1 = EARLY, 2 = LATE, 3 = MID
    # for (int i = 0; i < MODIFIER_PATTERNS.length; i++) {
    #   matcher = MODIFIER_PATTERNS[i].matcher(date);
    #   if (matcher.find()) {
    #     date = date.replace(matcher.group(), "");
    #     modifier = i + 1;
    #     break;
    #   }
    # }
    # date = date.trim();

    #  cases: XX
    try:
        d = roman.fromRoman(date)
        if d < 22:
            date += ' ' + lg.CENTURY_STANDARD
        else:
            date = str(d)
    except roman.InvalidRomanNumeralError:
        pass

    # French revolutionary calendar years
    # cases: an III, an IIIe, an deuxième
    if lang == 'fr' and date.lower().startswith('an '):
        y = re.sub('(?i)an ', '', date)

        try:
            d = roman.fromRoman(y.rstrip('e'))
            date = str(d + 1792)
        except roman.InvalidRomanNumeralError:
            try:
                d = int(re.sub(r'(ème|er)','', alpha2digit(y, lang='fr', ordinal_threshold=0)))
                date = str(d + 1792)
            except ValueError as e:
                pass

    # cases: 18th century, secolo XVI
    if lg.CENTURY_STANDARD in date:
        d = re.sub(lg.CENTURY_STANDARD, '', date).strip()
        d = re.sub(lg.ORDINALS, '', d).strip()

        n = None
        try:
            n = roman.fromRoman(d)
        except roman.InvalidRomanNumeralError:
            try:
                n = int(d)
            except ValueError:
                pass

        if n is not None:
            return str(n - 1) + 'XX' + sym
        #     startDate = str((n - 1) * 100 + 1)
        #     endDate = str(n * 100)
        #     endType = startType = XSD.gYear
        #     return startDate, endDate, startType, endType

    # // case 'early 18th century'
    # double[] itSpan = getItSpanFromModifier(modifier);

    # // case '1st half of the 18th century'
    # for (Pattern pat : CENTURY_PART_PATTERNS) {
    #   matcher = pat.matcher(date);
    #   if (!matcher.find()) continue;
    #   String itString = matcher.group(1);
    #   String partString = matcher.group(2);
    #   String centuryString = matcher.group(3);
    #   itSpan = getItSpanFromCentParts(itString, partString);
    #   if (centuryString.matches("\d{2}00s")) {
    #     century = getCenturyURI(centuryString.substring(0, 2) + "01");
    #   } else {
    #     if (RomanConverter.isRoman(centuryString)) centuryString += " secolo";
    #     century = VocabularyManager.searchInCategory(centuryString, null, "dates", false);
    #     if (century == null) { // this is a part, but of what?
    #       //System.out.println("Century not found: " + centuryString);
    #       return;
    #     }
    #   }
    # }
    # double it = itSpan[0];
    # double span = itSpan[1];
    #
    # if (century != null) {
    #   int cent = CENTURY_URI_MAP.inverseBidiMap().get(century) - 1;
    #
    #   int end = (int) Math.round(cent * 100 + span * it);
    #
    #   if (startYear == null) {
    #     it--;
    #     int start = (int) Math.round(cent * 100 + span * it + 1);
    #     startDate = startYear = padYear(start);
    #     startType = XSDDateType.XSDgYear;
    #   }
    #
    #   endDate = endYear = padYear(end);
    #   endType = XSDDateType.XSDgYear;
    #
    #   return;
    # }

    # cases: 1871, 1920s
    if re.match(SINGLE_YEAR, date):
        return date.rjust(4, '0').replace('0s', 'X') + sym

    YEAR_SPAN = r"(?i)(?:(?:" + lg.BETWEEN + r")\s+)?(\d{3,4}s?)(?:\s*(?:[-=\/]|" + \
                "|".join(lg.SEPARATORS) + r")\s*|[-=\/])(\d{2,4}s?)"

    # cases: 1741-1754,  1960s to 1970s, ...
    if re.fullmatch(YEAR_SPAN, date):
        matcher = re.search(YEAR_SPAN, date)

        start_year = matcher.group(1).replace('0s', 'X')
        end_year = matcher.group(2).replace('0s', 'X')
        if len(end_year) < len(start_year):
            end_year = start_year[0: len(start_year) - len(end_year)] + end_year

        return start_year + sym + '/' + end_year + sym

    # // case: 19th-20th century
    # if (date.matches(CENTURY_SPAN)) {
    #   matcher = CENTURY_SPAN_PATTERN.matcher(date);
    #   if (matcher.find()) {
    #     String startCentury = matcher.group(1).replace("th", "");
    #     String endCentury = matcher.group(2).replace("th", "");
    #     int startCent, endCent;
    #     if (RomanConverter.isRoman(startCentury))
    #       startCent = RomanConverter.toNumerical(startCentury);
    #     else startCent = parseInt(startCentury);
    #     if (RomanConverter.isRoman(endCentury))
    #       endCent = RomanConverter.toNumerical(endCentury);
    #     else endCent = parseInt(endCentury);
    #
    #     // maybe add a note that this is a century?
    #     startYear = padYear((startCent - 1) + "01");
    #     endYear = padYear(endCent + "00");
    #
    #     startType = XSDDateType.XSDgYear;
    #     endType = XSDDateType.XSDgYear;
    #     startDate = startYear;
    #     endDate = endYear;
    #   }
    #   return;
    # }

    DATE_REGEX = r"(?i)(?:(\d{1,2})(?:" + lg.ORDINALS + ")? )?(" + "|".join(lg.MONTHS) + r")(?: (\d{4}))?"

    # case "30 April 1856", "December 2004", "Fall 1919", "27th June"
    parsed = []
    for matcher in re.finditer(DATE_REGEX, date):
        dd = matcher.group(1)
        mm = matcher.group(2)
        yy = matcher.group(3)
        parsed.append(parse_matched_date(dd, mm, yy, lg.MONTHS))

    if len(parsed) > 0:
        return pack_edtf_list(parsed, sym)

    # case 31/07/1816
    try:
        dt = datetime.strptime(date, SLASH_LITTLE_ENDIAN)
        return dt.isoformat()
    except ValueError as e:
        # nothing to do
        pass

    # case 31/7/1816 , 13-9-67
    parsed = []
    for matcher in re.finditer(FULL_DATE_MULTI, date):
        dd = matcher.group(1)
        mm = int(matcher.group(2))
        yy = matcher.group(3)

        if len(dd) > 2:
            if len(yy) > 2:
                # I can't say which one is the year => I surrend
                continue
            else:  # swap
                temp = dd
                dd = yy
                yy = temp

        parsed.append(date_format(dd, mm, yy))

    if len(parsed) > 0:
        return pack_edtf_list(parsed, sym)

    # case 02/1877, 03/1881-04/1881
    parsed = []
    for matcher in re.finditer(MONTH_DATE_REGEX, date):
        mm = int(matcher.group(1))
        yy = matcher.group(2)

        parsed.append(date_format(None, mm, yy))

        yy = matcher.group(4)
        if yy is not None:
            mm = int(matcher.group(3))
            parsed.append(date_format(None, mm, yy))

    if len(parsed) > 0:
        return pack_edtf_list(parsed, sym)

    # if it is already EDTF
    if re.match('^[/0-9X-]*$', date):
        return date + sym

    # search month in string
    m = month_to_num(date, lg.MONTHS)
    if m != 0:
        return date_format(None, m, None) + sym

    return None


def get_parts_of_the_day(date, lang='en'):
    date = date.lower()
    lg = langs.get(lang, langs['en'])
    found = []
    for i, p in enumerate(lg.PART_OF_DAY):
        if re.search(p, date):
            found.append(langs['en'].PART_OF_DAY[i].replace("(^| )", ""))
    return found

# private static double[] getItSpanFromCentParts(String itString, String partString) {
#   double it = ordinalToInt(itString);
#   if (it == 0) {
#     return new double[]{-1, -1};
#   }
#   double span = 50; // half century
#   if (partString.matches("(third|tercio|1/3)")) {
#     span = 33.3;
#     if (it == -1) it = 3;
#   }
#   if (partString.matches("[qc]uart(o|er)?")) {
#     span = 25;
#     if (it == -1) it = 4;
#   }
#   if (partString.matches("ventennio")) {
#     span = 20;
#     if (it == -1) it = 5;
#   }
#   if (it == -1) it = 2;
#   return new double[]{it, span};
# }
#
# private static double[] getItSpanFromModifier(int modifier) {
#   double it = 1;
#   double span = 100;
#
#   // modifier: 0 = NONE, 1 = EARLY, 2 = LATE, 3 = MID
#   switch (modifier) {
#     case 1:
#       it = 1;
#       span = 25;
#       break;
#     case 2:
#       it = 4;
#       span = 25;
#       break;
#     case 3:
#       it = 1.5;
#       span = 50;
#   }
#   return new double[]{it, span};
# }
#


#   private static final String CENTURY_SPAN = "(\d{1,2}th|[XVI]+)(?: century| secolo)?\s*(?:[-=/]|to|or)\s*(\d{1,2}th|[XVI]+) (?:century|secolo)";
#   private static final Pattern CENTURY_SPAN_PATTERN = Pattern.compile(CENTURY_SPAN);
#   private static final String ES_CENTURY_SPAN = "(?i)s[ie]gl[oe]s? (\d{1,2})(?:-(\d{1,2}))?";
#   private static final Pattern ES_CENTURY_SPAN_PATTERN = Pattern.compile(ES_CENTURY_SPAN);
#
#   private static final String CENTURY_PART_EN = "(?i)((?:fir|1)st|(?:2|seco)nd|(?:3|thi)rd|fourth|last) (quarter|half|third),?(?: of(?: the)?)?";
#   private static final String CENTURY_PART_IT = "(?i)(?:(prim|second|terz|ultim|I+)[oa]?) (ventennio|quarto|metAAA)(?: del)?";
#   private static final String CENTURY_PART_ES = "(?i)([1234][]|pr?i[mn]era?|segund[oa]|segon|tercer|UUUltimo?) (cuarto|quart|mitad|meitat|tercio|1/3)(?: del)?";
#   private static final String CENTURY_PART_FR = "(?i)(1[EEEe]re?|[234]d?e) (quart|moitiEE)(?: du)?";
#   private static final Pattern CENTURY_PART_EN_PATTERN = Pattern.compile(CENTURY_PART_EN + " (.+)");
#   private static final Pattern CENTURY_PART_IT_PATTERN = Pattern.compile(CENTURY_PART_IT + " (.+)");
#   private static final Pattern CENTURY_PART_ES_PATTERN = Pattern.compile(CENTURY_PART_ES + " (.+)");
#   private static final Pattern CENTURY_PART_FR_PATTERN = Pattern.compile(CENTURY_PART_FR + " (.+)");
#   private static final Pattern[] CENTURY_PART_PATTERNS = {CENTURY_PART_EN_PATTERN, CENTURY_PART_ES_PATTERN, CENTURY_PART_IT_PATTERN, CENTURY_PART_FR_PATTERN};
#   private static final String EARLY_REGEX = "(?i)(inizio?|dEEEbut|early|(?:p[ri]+n?cipi|inici?)o(?:s)?)(?: del?| du)?";
#   private static final String LATE_REGEX = "(?i)(?:very )?(late|fin(?:e|ale?s)?)(?: del?| du)?";
#   private static final String MID_REGEX = "(?i)(mid(-| |dle)|milieu|^metAAAA|second or third quarter of|^mitad|to mid-twentieth century|(?:a )?m+ediados|a mitjan)(?: del?| du)?";
#   private static final Pattern EARLY_PATTERN = Pattern.compile(EARLY_REGEX);
#   private static final Pattern LATE_PATTERN = Pattern.compile(LATE_REGEX);
#   private static final Pattern MID_PATTERN = Pattern.compile(MID_REGEX);
#   private static final Pattern[] MODIFIER_PATTERNS = {EARLY_PATTERN, LATE_PATTERN, MID_PATTERN};
#
#   public static final String[] CENTURY_PART_REGEXES = {CENTURY_PART_EN, CENTURY_PART_ES, CENTURY_PART_IT, CENTURY_PART_FR, EARLY_REGEX, LATE_REGEX, MID_REGEX};
#
#   private static final String DATE_ES_REGEX = "(?i)(?<!\d)(\d{1,2})?\s?(?:de |-)?(ene(?:ro)?|feb(?:r|re+ro?)?|mar(?:[zc]o)?|abr(?:il)?|may(?:[o0])?|jun(?:io)?|jul(?:iol?)?|ago(?:sto)?|se[pt](?:tiembre)?|oct(?:ubre)?|nov(?:i?embre)?|dic(?:iembre)?)\.?\s?(?:de |-)?(\d{2,4})";
#   private static final Pattern DATE_ES_PATTERN = Pattern.compile(DATE_ES_REGEX);
#   private static final String[] MONTHS_ES = {"enero", "febrero", "marzo", "abril", "mayo",
#     "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
#   };
#   private static final String DATE_FR_REGEX = "(?i)(?<!\d)(\d{1,2})?\s?(?:de |-)?(janvier|f[EEEe][vb]rier|mars|avril|mai|juin|juillet|aoUUUt|septembre|octobre|november|dEEEcembre)\.?\s?(\d{4})";
#   private static final Pattern DATE_FR_PATTERN = Pattern.compile(DATE_FR_REGEX);
#   private static final String[] MONTHS_FR = {"janvier", "fevrier", "mars", "avril", "mai",
#     "juin", "juillet", "aoUUUt", "septembre", "octobre", "novembre", "dEEcembre"
#   };
#
#
#
#   private static final String DECADES_ES_REGEX = "(?i)(?:dEEcada de lo|aNNo)(s)? (\d+|diez)(?:-(\d+))?(?: del|,)?(?: sig(?:lo|\.) ?([XIV]+))?( \d+$)?";
#   private static final Pattern DECADES_ES_PATTERN = Pattern.compile(DECADES_ES_REGEX);
#
#
#
#   public static final String BEFORE_CHRIST = "(BC|aC|a$)";
#
#
#
#   private static final BidiMap<Integer, Resource> CENTURY_URI_MAP;
#
#   private static final String BEFORE_REGEX = "(?i)(or earlier|before)";
#   private static final Pattern BEFORE_PATTERN = Pattern.compile(BEFORE_REGEX);
#   private static final String AFTER_REGEX = "(?i)(or later|after)";
#   private static final Pattern AFTER_PATTERN = Pattern.compile(AFTER_REGEX);
#
#   public static final String ACTIVITY_REGEX = "(?i)\((embroider(ed|y|ing)|used|made|published|drawn|designed( and made| \(process\))?|(block )?print(ed|ing)|tambouring|collected|sewing|worn|altered|purchased|manufactured|(hand |tapestry )?weaving|woven|quilted|paint(ing|ed)|retailed|joinery|sold|upholstered)\)";
#   public static final Pattern ACTIVITY_PATTERN = Pattern.compile(ACTIVITY_REGEX);
#
#   static {
#     BidiMap<Integer, Resource> map = new DualHashBidiMap<>();
#
#     map.put(4, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404496"));
#     map.put(5, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404497"));
#     map.put(6, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404498"));
#     map.put(7, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404499"));
#     map.put(8, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404500"));
#     map.put(9, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404501"));
#     map.put(10, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404502"));
#     map.put(11, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404503"));
#     map.put(12, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404504"));
#     map.put(13, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404505"));
#     map.put(14, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404506"));
#     map.put(15, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404465"));
#     map.put(16, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404510"));
#     map.put(17, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404511"));
#     map.put(18, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404512"));
#     map.put(19, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404513"));
#     map.put(20, ResourceFactory.createResource("http://vocab.getty.edu/aat/300404514"));
#     CENTURY_URI_MAP = map;
#   }
#
#   public static final List<String> activityList = new ArrayList<>();
#
#   public static final Model centralModel = ModelFactory.createDefaultModel();
#
#   private String startYear, startMonth, startDay;
#   private String endYear, endMonth, endDay;
#   private String startDate, endDate;
#   private String label;
#   private XSDDatatype startType, endType;
#   private String vocabularyMatch;
#   private boolean splitted;
#   private boolean startApproximate, endApproximate;
#   private boolean startUncertain, endUncertain;
#   private int before_after;
#
#   public TimeSpan() {
#     super();
#
#     this.model = centralModel;
#     this.vocabularyMatch = null;
#     this.splitted = false;
#     this.label = null;
#     before_after = 0;
#   }
#
#   public TimeSpan(Date date) {
#     this();
#     ISO_DATE_FORMAT.setTimeZone(UCT);
#
#     this.label = ISO_DATE_FORMAT.format(date).substring(0, 10);
#     this.startDate = this.endDate = label;
#     this.startYear = this.endYear = label.substring(0, 4);
#     this.startType = this.endType = XSDDatatype.XSDdate;
#   }
#
#   public TimeSpan(String date) {
#     this();
#     if (StringUtils.isBlank(date)) return;
#
#     Matcher m = ACTIVITY_PATTERN.matcher(date);
#     if (m.find()) {
#       String activity = m.group(1);
#       activityList.add(activity);
#       date = date.replaceAll(ACTIVITY_REGEX, "");
#     }
#     date = date.replaceAll("(?i)^dated ", " ");
#     date = date.replaceAll("(?i)\(dated\) ", " ");
#
#     this.label = date;
#
#     // Parsing the date
#     parseDate(date);
#     if (this.vocabularyMatch == null && this.startDate == null) {
#       this.splitted = true;
#       // try again separating the parts
#       for (String p : date.split(SEPARATORS, 2))
#         parseDate(p);
#     }
#   }
#
#   public TimeSpan(int start, int end) {
#     this();
#     startYear = startDate = padYear(start);
#     endYear = endDate = padYear(end);
#     startType = endType = XSDDateType.XSDgYear;
#   }
#
#   public TimeSpan(String start, String end) {
#     this();
#     if (!StringUtils.isBlank(start))
#       startYear = startDate = padYear(start);
#     if (!StringUtils.isBlank(end))
#       endYear = endDate = padYear(end);
#     startType = endType = XSDDateType.XSDgYear;
#   }
#
#   public void createResource() {
#     if (this.vocabularyMatch != null) {
#       this.resource = model.createResource(this.vocabularyMatch);
#       return;
#     }
#
#     String edtf = getEDTF();
#     String seed = edtf != null ? edtf : this.label;
#     if (seed == null) return; // null timespan
#
#     String uri;
#     if (startDate != null && endDate != null && !hasModifiers())
#       uri = ConstructURI.transparent(this.className, seed);
#     else uri = ConstructURI.build(this.className, seed);
#
#     this.resource = model.createResource(uri);
#     this.setClass(CIDOC.E52_Time_Span);
#     this.addProperty(CIDOC.P78_is_identified_by, label);
#     this.addProperty(SKOS.prefLabel, seed.replace("/", " / "));
#
#     if (edtf == null) return; // no start date AND no end date
#     this.addProperty(RDFS.label, edtf);
#
#     String start = startDate;
#     String end = endDate;
#     if (before_after == 2) {
#       start = endDate;
#       end = null;
#     } else if (before_after == -2) {
#       start = null;
#       end = startDate;
#     }
#
#     Resource startInstant = makeInstant(start, startType, uri + "/start");
#     Resource endInstant = makeInstant(end, endType, uri + "/end");
#
#     this.addProperty(Time.hasBeginning, startInstant);
#     this.addProperty(CIDOC.P86_falls_within, getCenturyURI(startYear));
#
#     this.addProperty(Time.hasEnd, endInstant);
#     this.addProperty(CIDOC.P86_falls_within, getCenturyURI(endYear));
#     // WARNING: in cases like 1691-1721, the TS is linked both to 17th and 18th century
#     // (even if formally not 100% correct)
#   }
#

#

#
#


#
#
#
#   /**
#    * Convert ordinal literals (e.g. first, second, ...) in related int.
#    * Four langs: EN, ES, IT, FR
#    *
#    * @param ordinal number (e.g. "primo", "first", "1st")
#    * @return related integer, -1 if ordinal is "last", 0 if not recognised
#    */
#   private static int ordinalToInt(@NotNull String ordinal) {
#     String ordinalMin = ordinal.replaceAll("[oa]", "").toUpperCase();
#     ordinal = ordinal.toLowerCase();
#
#     if (RomanConverter.isRoman(ordinalMin)) {
#       return RomanConverter.toNumerical(ordinalMin);
#     }
#     if (ordinal.equals("first") || ordinal.startsWith("pri") || ordinal.startsWith("pimer"))
#       return 1;
#     if (ordinal.matches("(se(co|gu)nd[oa]?|segon)"))
#       return 2;
#     if (ordinal.matches("(third|terz|tercer)"))
#       return 3;
#     if (ordinal.equals("fourth"))
#       return 4;
#     if (ordinal.matches("(last|[UUUu]ltimo?)"))
#       return -1;
#     ordinal = ordinal.replaceAll("\D+", ""); // replace all non-digits
#     try {
#       return parseInt(ordinal);
#     } catch (NumberFormatException e) {
#       return 0;
#     }
#   }
#
#   private static Resource getCenturyURI(String year) {
#     if (year == null) return null;
#     int x = (parseInt(year) + 99) / 100;
#     return CENTURY_URI_MAP.getOrDefault(x, null);
#   }
#
#   @Nullable
#   private Resource makeInstant(@NotNull String date, XSDDatatype type, String uri) {
#     if (StringUtils.isBlank(date) || !date.matches(UCT_DATE_REGEX)) return null;
#
#     return this.model.createResource(uri)
#       .addProperty(RDF.type, Time.Instant)
#       .addProperty(Time.inXSDDate, this.model.createTypedLiteral(date, type));
#   }
#
#   public void setLabel(String label) {
#     this.label = label;
#     if (this.resource != null)
#       this.addProperty(CIDOC.P78_is_identified_by, label);
#   }
#
#   static Date dateFromString(String value, @NotNull DateFormat format) throws ParseException {
#     format.setTimeZone(UCT);
#     return format.parse(value);
#   }
#
#   private boolean hasModifiers() {
#     return startApproximate || endApproximate || endUncertain || startUncertain || before_after != 0;
#   }
#
#   public void setUncertain(boolean uncertain) {
#     this.startUncertain = this.endUncertain = uncertain;
#   }
#
#   public void setApproximate(boolean approximate) {
#     this.startApproximate = this.endApproximate = approximate;
#   }
#
#   public static TimeSpan parseVenezia(String start, String end, String fraction, String century) {
#     String[] labelParts = {century, fraction, start, end};
#     String label = Arrays.stream(labelParts)
#       .filter(s -> (s != null && s.length() > 0))
#       .collect(Collectors.joining(", "));
#
#     TimeSpan ts;
#
#     if (start == null) {
#       if (century.contains("/")) {
#         String[] p = century.split("/");
#         int startCentury = RomanConverter.toNumerical(p[0].trim());
#         int endCentury = RomanConverter.toNumerical(p[1].trim());
#
#         double itStart = -1;
#         double spanStart = -1;
#         double itEnd = -1;
#         double spanEnd = -1;
#
#         if (fraction != null && fraction.contains("/")) {
#           String[] f = fraction.split("/");
#
#           int modifier = 0; // 0 = NONE, 1 = EARLY, 2 = LATE, 3 = MID
#           for (int i = 0; i < MODIFIER_PATTERNS.length; i++) {
#             Matcher matcher = MODIFIER_PATTERNS[i].matcher(f[0]);
#             if (matcher.find()) {
#               modifier = i + 1;
#               break;
#             }
#           }
#           double[] itSpan = getItSpanFromModifier(modifier);
#           itStart = itSpan[0];
#           spanStart = itSpan[1];
#
#           for (int i = 0; i < MODIFIER_PATTERNS.length; i++) {
#             Matcher matcher = MODIFIER_PATTERNS[i].matcher(f[1]);
#             if (matcher.find()) {
#               modifier = i + 1;
#               break;
#             }
#           }
#           itSpan = getItSpanFromModifier(modifier);
#           itEnd = itSpan[0];
#           spanEnd = itSpan[1];
#         }
#
#         int startY, endY;
#         if (itStart > 0 && spanStart > 0 && itEnd > 0 && spanEnd > 0) {
#           endY = (int) Math.round(endCentury * 100 + spanEnd * itEnd);
#           startY = (int) Math.round(startCentury * 100 + spanStart * (itStart - 1) + 1);
#         } else {
#           endY = Math.round(endCentury * 100);
#           startY = Math.round((startCentury - 1) * 100 + 1);
#         }
#         ts = new TimeSpan(startY, endY);
#         ts.setLabel(label);
#         return ts;
#       }
#       if (fraction != null) century = fraction + " " + century;
#       ts = new TimeSpan(century);
#       ts.setLabel(label);
#       return ts;
#     }
#
#
#     boolean approximate = false;
#     boolean uncertain = false;
#     Matcher matcher = APPROXIMATE_PATTERN.matcher(start);
#     if (matcher.find()) {
#       approximate = true;
#       start = start.replaceAll(APPROXIMATE_REGEX, " ");
#     }
#
#     matcher = UNCERTAIN_PATTERN.matcher(start);
#     if (matcher.find()) {
#       uncertain = true;
#       start = start.replaceAll(UNCERTAIN_REGEX, "");
#     }
#     for (String x : new String[]{CENTURY_PART_IT, EARLY_REGEX, MID_REGEX, LATE_REGEX}) {
#       if (start.matches(x)) {
#         start += " " + century;
#         if (!start.contains("sec")) start += " secolo";
#         ts = new TimeSpan(start);
#         ts.setUncertain(uncertain);
#         ts.setApproximate(approximate);
#         ts.setLabel(label);
#         return ts;
#       }
#     }
#
#     if (end != null) {
#       boolean approximateEnd = false;
#       boolean uncertainEnd = false;
#
#       matcher = APPROXIMATE_PATTERN.matcher(end);
#       if (matcher.find()) {
#         approximateEnd = true;
#         end = end.replaceAll(APPROXIMATE_REGEX, " ");
#       }
#
#       matcher = UNCERTAIN_PATTERN.matcher(end);
#       if (matcher.find()) {
#         uncertainEnd = true;
#         end = end.replaceAll(UNCERTAIN_REGEX, "");
#       }
#
#       ts = new TimeSpan(start + " - " + end);
#       ts.startApproximate = approximate;
#       ts.endApproximate = approximateEnd;
#       ts.startUncertain = uncertain;
#       ts.endUncertain = uncertainEnd;
#     } else {
#       ts = new TimeSpan(start);
#       ts.setUncertain(uncertain);
#       ts.setApproximate(approximate);
#     }
#
#     ts.setLabel(label);
#     return ts;
#   }
#
#   public String getStartDate() {
#     return startDate;
#   }
# }
