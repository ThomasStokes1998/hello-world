# Imports
import pandas as pd
from datetime import date
from activity_code import activity_code, athome_students, misc, in_active  # Keeping student names anonymous

# Dictionaries
activities_dict = {}
sm_dict = {}
init_dict = {}
assessment_dict = {}
year_dict = {}


# Functions
# Converts each name into the displayed format
def nameFormat(names):
    formatted = []
    for name in names:
        n = name.split(" ")
        fname = n[0]
        lname = n[1]
        if fname == misc[0]:
            nom = fname + " " + lname[:2]
        elif "-" in lname:
            x = lname.split("-")
            if len(x[1]) > 0:
                nom = fname + " " + x[0][0] + x[1][0]
            else:
                nom = fname + " " + x[0][0]
        else:
            nom = fname + " " + lname[0]
        formatted.append(nom)
    return formatted


# Calculates the assessment score for each student
def assessmentScore(init_level, curr_level):
    if curr_level > 10:
        if init_level > 10:
            score = (curr_level - init_level) * 10
        else:
            score = (curr_level - 10) * 10 + (10 - init_level) * 5
    else:
        score = (curr_level - init_level) * 5
    return round(score, 3)


# Calculates the next date
def nextDate(curr_date):
    x = curr_date.split("_")
    d = int(x[0])
    m = int(x[1])
    if d == 31:
        d = 1
        m += 1
    else:
        d += 1
    ds = str(d)
    dm = str(m)
    if d < 10:
        ds = "0" + ds
    if m < 10:
        dm = "0" + dm
    return ds + "_" + dm


# Calculates the number of days since July 1st
def indexNumber(curr_date) -> int:
    x = curr_date.split("_")
    d = int(x[0])
    m = int(x[1])
    da = date(2021, m, d)
    dt = da - date(2021, 7, 1)
    return dt.days


# Cleans the assessment excel files
def ar_clean(a):
    ar = pd.read_excel(a)
    if "Year" not in list(ar.columns):
        ar.rename(columns={"Grade": "Year"}, inplace=True)
    ar["Name"] = ar["Student First Name"] + " " + ar["Student Last Name"]
    ar["Name"] = nameFormat(ar["Name"])
    ar = ar.drop(["Student First Name", "Student Last Name"], axis=1)
    ar["Assessment Level"] = ar["Assessment Level"].fillna(-10)
    ar = ar[["Name", "Assessment Level", "Assessment Title", "Pre/Post", "Score", "Date Taken", "Year"]]
    ar["Assessment Level"].unique()

    def alevel(x):
        al = []
        for n in x:
            if n == "NF":
                al.append(0)
            elif n == "GF":
                al.append(0)
            elif "EXT" in str(n):
                al.append(int(n[-1]))
            else:
                al.append(int(n))
        return al

    ar["Assessment Level"] = alevel(ar["Assessment Level"])
    ar["Score"] = ar["Score"].fillna(0)
    ar = ar[ar["Assessment Level"] >= 0].reset_index(drop="index")
    return ar


# Updates Students Assessment Score
def student_score(xy, ddex=None, start=False):
    students = xy['Name'].unique()
    students = list(students)
    for student in students:
        data = xy[xy["Name"] == student].reset_index(drop="index")
        t = len(data)
        max_al = max(list(data["Assessment Level"]))
        # Ensures the highest assessment level is picked
        data = data[data["Assessment Level"] == max_al].reset_index(drop="index")
        max_score = data["Score"][0]
        if data["Assessment Title"][0] == "Mathnasium Assessment 10 F":
            max_score = max_score * 2 / 3
        for i in range(len(data["Name"])):
            ds = data["Score"][i]
            if data["Assessment Title"][i] == "Mathnasium Assessment 10 F":
                ds = ds * 2 / 3
            if ds > max_score:
                max_score = ds
                max_al = data["Assessment Level"][i]
        # Calculating the assessment level
        max_level = max_al + max_score
        max_level = round(max_level, 3)
        if student == misc[1]:
            max_level = 11
        # Adding new students
        if start:
            assessment_dict[student] = [0] * l
            sm_dict[student] = [0] * l
            activities_dict[student] = [0] * l
            if student == misc[2]:
                init_dict[student] = 6.377
            elif max_level < 1:
                init_dict[student] = 1
            else:
                init_dict[student] = max_level
        if not start:
            if student not in list(init_dict.keys()):
                init_dict[student] = max_level
                if student not in list(sm_dict.keys()):
                    sm_dict[student] = [0] * l
                assessment_dict[student] = [0] * l
                activities_dict[student] = [0] * l
            # Updating assessment scores
            elif max_level > init_dict[student]:
                s = assessmentScore(init_dict[student], max_level)
                if s > assessment_dict[student][ddex]:
                    for i in range(l):
                        if i >= ddex:
                            assessment_dict[student][i] = s


# Finds the index and points for a given code
def activityDecoder(code):
    pp = code % 100
    mm = ((code - pp) % 10_000) / 100
    dd = (code - (mm * 100 + pp)) / 10_000
    dt = date(2021, int(mm), int(dd)) - date(2021, 7, 1)
    return dt.days, int(pp)


# All the dates for the leaderboard
leaderboard_dates = ["01_07"]
x = "01_07"
while x != "04_09":
    leaderboard_dates.append(nextDate(x))
    x = leaderboard_dates[-1]

l = len(leaderboard_dates)
# print(leaderboard_dates)

# Initial assessment scores
init_ar = ar_clean("Assessments/AR 30_06_2021.xlsx")
student_score(init_ar, start=True)

# Main Loop
wd = date.today()
if wd.day < 10:
    d = "0" + str(wd.day)
else:
    d = str(wd.day)
if wd.month < 10:
    m = "0" + str(wd.month)
else:
    m = str(wd.month)
tdate = d + "_" + m
for ld in leaderboard_dates:
    if ld == tdate:
        break
    print("Started " + ld)
    ddex = indexNumber(ld)
    # Update the assessment scores
    if ddex < indexNumber("19_08"):
        ar = ar_clean("Assessments/Assessment Report from 01_01_2021 to " + ld + "_2021  19_08_2021.xlsx")
    else:
        ar = ar_clean(
            "Assessments/Assessment Report from 01_01_2021 to " + ld + "_2021  " + nextDate(ld) + "_2021.xlsx")
    student_score(ar, ddex=ddex)
    # Update the number of skills mastered
    if ddex < indexNumber("19_08"):
        df = pd.read_excel("Reports/Student Report From 01_07_2021 To " + ld + "_2021  19_08_2021.xlsx")
    else:
        df = pd.read_excel("Reports/Student Report From 01_07_2021 To " + ld + "_2021  " + nextDate(ld) + "_2021.xlsx")
    df["Name"] = nameFormat(df["Student Name"])
    for i in range(len(df["Name"])):
        if df["Enrolment Status"][i] == "Enrolment" or df["Enrolment Status"][i] == "On Hold":
            student = df["Name"][i]
            sm = df["Skills Mastered"][i]
            if student == misc[1] and ld == "31_07":
                sm = 4
            if student not in list(year_dict.keys()):
                if student == misc[3]:
                    year_dict[student] = 11
                else:
                    year_dict[student] = df["Year"][i]
            if student not in list(init_dict.keys()):
                sm_dict[student] = [0] * l
            if sm > sm_dict[student][ddex]:
                for i in range(l):
                    if i >= ddex:
                        sm_dict[student][i] = sm

# Create the activity dictionary
earners = list(activity_code.keys())
for earner in earners:
    points = activity_code[earner]
    for code in points:
        ddex, pp = activityDecoder(code)
        for i in range(l):
            if i >= ddex:
                activities_dict[earner][i] = pp

# Calculate the Total score = skills mastered + activities + assessment score
students = list(init_dict.keys())
y = []
for student in students:
    if student not in list(year_dict.keys()):
        y.append("6")
    else:
        y.append(year_dict[student])
lbc = pd.DataFrame({"Name": students, "Year": y})
for i in range(l):
    d = leaderboard_dates[i]
    x = []
    for student in students:
        if student in athome_students:
            x.append(0)
        elif d[-1] == "9" and student in in_active:
            x.append(0)
        else:
            s = sm_dict[student][i]
            ac = activities_dict[student][i]
            asc = assessment_dict[student][i]
            p = s + ac + asc
            x.append(round(p, 3))
    lbc[d] = x

lbc = lbc.sort_values("Name").reset_index(drop="index")
lbc.to_csv("Lboard_bar_chart.csv", index=False)
lbc[["Name", tdate]].to_csv("lboard_sheets_" + tdate + ".csv", index=False)

# Creating the weekly leaderboard
if date.today().weekday() == 0:
    m = indexNumber(tdate)
    l = leaderboard_dates[m-7]
    n = lbc["Name"]
    points = []
    for i in range(len(lbc)):
        if n[i] in athome_students:
            points.append(0)
        else:
            p = lbc[tdate][i] - lbc[l][i]
            points.append(round(p, 3))
    wl = pd.DataFrame({"Name": n, "Points": points})
    wl.to_csv("Weekly_Lboard_" + tdate + ".csv", index=False)
