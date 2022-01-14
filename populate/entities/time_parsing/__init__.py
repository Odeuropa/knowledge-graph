from rdflib import XSD

from . import it, en


def date_format(dd, m, yy):
    if len(yy) == 2:
        yy = "19" + yy

    _type = XSD.gMonth
    formatted = yy + "-" + "%02d" % int(m)
    if dd:
        _type = XSD.date
        formatted += "-" + "%02d" % int(dd)

    return formatted, _type


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
