import re
from rdflib import XSD
from datetime import datetime

UCT_DATE_REGEX = r"\d{4}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|[1-2]\d|3[0-1]))?)?(?:T(?:[0-1]\d|2[0-3]):[0-5]\d:[" \
                 "0-5]\dZ?)?"

ISO_DATE_FORMAT = "yyyy-MM-dd"
SLASH_LITTLE_ENDIAN = "%d/%m/%Y"

ANY_BRACKETS = r"[(\[\])]"

APPROXIMATE_REGEX = r'(?i)(circa|around|about|vers |(?<!d)ca?\.|\[ca]|^ca |ca$)'
UNCERTAIN_REGEX = r"(?i)(forse|posiblemente|(proba|possi)ba?ly|\?|¿)"

SINGLE_YEAR = r"\d{3,4}s?"
YEAR_SPAN = r"(?i)(?:(?:entre|between)\s+)?(\d{3,4}s?)(?:\s*(?:[-=\/]|to|a|or|y|and)\s*|[-=\/])(\d{2,4}s?)"

FULL_DATE_MULTI = r"(3[01]|[012]?[0-9]|\d{3,4})[-/ .](1[012]|0?\d)[-/ .](\d{2,4})"
MONTH_DATE_REGEX = r"(?:(\d{2})/(\d{4}))(?:-(\d{2})/(\d{4}))?"

SEPARATORS = "(?:[-=/]| to | a | or | y | and )"

DATE_EN_REGEX = r"(?i)(january|february|march|april|may|june|july|august|september|october|november|december|spring" \
                r"|fall|winter|summer)(?: (\d{1,2}))? (\d{4})"
MONTHS_EN = ["january", "february", "march", "april", "may",
             "june", "july", "august", "september", "october", "november", "december",
             "spring", "summer", "fall", "winter"]


def format(dd, m, yy):
    if len(yy) == 2:
        yy = "19" + yy

    _type = XSD.gMonth
    formatted = yy + "-" + "%02d" % int(m)
    if dd:
        _type = XSD.date
        formatted += "-" + "%02d" % int(dd)

    return formatted, _type


#         def getEDTF() {
#     if (startDate == null && endDate == null)
#       return null;
#
#     String startSym = "", endSym = "";
#     if (startUncertain && startApproximate) startSym = "%";
#     else if (startUncertain) startSym = "?";
#     else if (startApproximate) startSym = "~";
#     if (endUncertain && endApproximate) endSym = "%";
#     else if (endUncertain) endSym = "?";
#     else if (endApproximate) endSym = "~";
#
#     String bf = "", af = "";
#     // 0 = NONE, +1 = ON OR AFTER, +2 = AFTER, -1 = ON OR BEFORE, -2 = BEFORE
#     if (before_after > 0) af = "..";
#     else if (before_after < 0) bf = "..";
#
#     String edtf;
#     if (this.startDate != null) {
#       if (startDate.equals(endDate) && startUncertain == endUncertain && endApproximate == startApproximate)
#         edtf = bf + startDate + af + startSym;
#       else if (endDate != null)
#         if (before_after == 2) {
#           edtf = endDate + endSym + "/..";
#         } else if (before_after == -2) {
#           edtf = "../" + startDate + startSym;
#         } else edtf = bf + startDate + startSym + "/" + endDate + af + endSym;
#       else edtf = bf + startDate + af + startSym + "/";
#     } else edtf = "/" + bf + endDate + af + endSym;
#
#     return edtf;

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


def parse_date(date):
    startYear = None
    startDate = None
    startType = None
    endYear = None
    endDate = None
    endType = None

    matcher = re.search(APPROXIMATE_REGEX, date)
    approximate = True if matcher else False
    if approximate:
        date = re.sub(APPROXIMATE_REGEX, " ", date)

    matcher = re.search(UNCERTAIN_REGEX, date)
    uncertain = True if matcher else False
    if uncertain:
        date = re.sub(UNCERTAIN_REGEX, " ", date)

    # preliminary parsing
    date = re.sub("(?i)^(in|on)( the)? ", "", date)  # in November
    date = re.sub("\(.*\)", "", date)  # curly brackets
    date = re.sub("\[.*]", "", date)  # square brackets
    date = re.sub(ANY_BRACKETS, "", date)  # orphan brackets

    date = re.sub("\"", "", date)
    date = date.strip()
    if not date:
        return None

    date = re.sub(" A.?D.?", "", date);
    date = re.sub(" CE$", "", date);
    date = re.sub(" CE-", "-", date);
    date = re.sub("dC\.?$", "", date);
    date = re.sub(" d$", "", date);
    date = re.sub("^by ", "", date);
    date = re.sub("soglo", "siglo", date);
    date = re.sub("sec.", "secolo", date)
    date = re.sub("(?i)s(ig)?\. ?", "siglo ", date)
    date = re.sub("(?i)se? ([XVI]+)", "siglo $1", date)
    date = re.sub(" ca$", " ", date);
    date = re.sub("^ca ", " ", date);

    date = re.sub("'s", "s", date)
    date = re.sub("centuries", "century", date)

    date = re.sub("[.,]$", "", date)  # trailing punctuation
    date = re.sub("\s+", " ", date)  # double space to one space

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

    # // cases: XX
    # if (RomanConverter.isRoman(date)) date += " secolo";
    #
    # // cases: 18th century, secolo XVI
    # Resource century = VocabularyManager.searchInCategory(date, null, "dates", false);
    # if (century != null && modifier == 0 && !splitted && !hasModifiers()) {
    #   this.vocabularyMatch = century.getURI();
    #   return;
    # }

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
    if re.fullmatch(SINGLE_YEAR, date):
        if startYear is None:
            startYear = startDate = decade2year(date, False, modifier)
            startType = XSD.gYear

        endYear = endDate = decade2year(date, True, modifier)
        endType = XSD.gYear
        return startDate, endDate, startType, endType

    # cases: 1741-1754,  1960s to 1970s, ...
    if re.fullmatch(YEAR_SPAN, date):
        matcher = re.search(YEAR_SPAN, date)
        if matcher:
            sy = decade2year(matcher.group(1), False, modifier)
            if startYear is None:
                startDate = startYear = sy
                startType = XSD.gYear

            endYear = matcher.group(2)

            if len(endYear) < len(sy):
                endYear = sy.substring(0, sy.length() - len(endYear)) + endYear

            endDate = endYear = decade2year(endYear, True, modifier)
            endType = XSD.gYear

            return startDate, endDate, startType, endType

        return None

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

    # case "April 30 1856", "December 2004", "Fall 1919"
    for matcher in re.finditer(DATE_EN_REGEX, date):
        dd = matcher.group(2)
        mm = matcher.group(1)
        yy = matcher.group(3)
        mi = 0
        for i, m in enumerate(MONTHS_EN):
            mi = i
            if mm.lower() == m:
                break
        mi += 1

        if mi <= 12:
            if not startDate:
                startDate, startType = format(dd, mi, yy)
            endDate, endType = format(dd, mi, yy)
        else:
            if mi == 13:  # Spring
                if not startDate:
                    startDate, startType = format('21', 3, yy)
                endDate, endType = format("21", 6, yy)
            if mi == 14:  # Summer
                if not startDate:
                    startDate, startType = format('22', 6, yy)
                endDate, endType = format("22", 9, yy)
            if mi == 15:  # Fall
                if not startDate:
                    startDate, startType = format('23', 9, yy)
                endDate, endType = format("22", 12, yy)
            if mi == 16:  # Winter
                if not startDate:
                    startDate, startType = format('23', 12, yy)
                endDate, endType = format("20", 3, str(int(yy) + 1))

    if startDate:
        return startDate, endDate, startType, endType

        # case 31/07/1816
    try:
        dt = datetime.strptime(date, SLASH_LITTLE_ENDIAN)
        text = dt.isoformat()
        startDate = text
        endDate = text
        startYear = text.sub(0, 4)
        endYear = startYear

        startType = XSD.date
        endType = XSD.date
        return startDate, endDate, startType, endType
    except ValueError as e:
        # nothing to do
        pass

    # case 31/7/1816 , 13-9-67
    for matcher in re.finditer(FULL_DATE_MULTI, date):
        dd = matcher.group(1)
        mm = int(matcher.group(2))
        yy = matcher.group(3)

        if len(dd) > 2:
            if len(yy) > 2:
                continue
            else:  # swap
                temp = dd
                dd = yy
                yy = temp

        if len(yy) == 3:
            yy = "1" + yy
        elif len(yy) == 2:
            yy = "19" + yy

        if startDate is None:
            startDate, startType = format(dd, mm, yy)
        endDate, endType = format(dd, mm, yy)
    if startDate is not None:
        return startDate, endDate, startType, endType

    # case 02/1877, 03/1881-04/1881
    for matcher in re.finditer(MONTH_DATE_REGEX, date):
        mm = int(matcher.group(1))
        yy = matcher.group(2)

        if startDate is None:
            startDate, startType = format(None, mm, yy)

        endDate, endType = format(None, mm, yy)

        yy = matcher.group(4)
        if yy is not None:
            mm = int(matcher.group(3))
            endDate, endType = format(None, mm, yy)

    if startDate is not None:
        return startDate, endDate, startType, endType

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
