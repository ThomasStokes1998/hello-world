import pandas as pd
from datetime import date


class Radius:
    def __init__(self, sheet, home):
        # Student Report Variables
        self.sheet = sheet
        self.df = pd.read_excel(sheet)
        self.sr = self.df[['Student Name', 'Last Attendance', 'Last Assessment']]
        self.idle = ['Bea Navarro Grail - B12', 'Johnny Pearson - B8', 'Lehna Bains - B12']
        self.enrolled = len(self.sr['Student Name'])
        self.today = date.today()
        # AtHome Variables
        if home != "":
            self.athome = home
            self.home = pd.read_excel(self.athome)
            self.home['Name'] = self.home['First Name'] + ' ' + self.home['Last Name']
            self.home = self.home.drop(['Archivable Students', 'First Name', 'Last Name'], axis=1)

    # Finds all the students that haven't been in for at least two weeks
    def attendance(self, debug=False):
        nom = []
        tw_la = []
        tw_days = []
        if debug:
            weird = []
        for i in range(self.enrolled):
            n = self.sr['Student Name'][i]
            x = self.sr['Last Attendance'][i]
            y = x.split('/')
            # Finds how ling it has been since the student last attended
            if len(y) > 1 and n not in self.idle:
                day = y[0]
                month = y[1]
                last_date = date(2021, int(month), int(day))
                diff = self.today - last_date
                r = str(diff).split(' ')
                # Finds if the student has been here for more than 14 days
                if len(r) > 2 and int(r[0]) >= 14:
                    nom.append(n)
                    tw_la.append(x)
                    tw_days.append(int(str(diff).split(' ')[0]))
            # Saves students who don't have a date
            elif debug and n not in self.idle:
                weird.append(n)
                weird.append(x)
        # Creating the DataFrames
        if len(nom) == 0:
            print('No Students')
        else:
            tw = pd.DataFrame({'Name': nom, 'Last Attendance': tw_la, 'Days': tw_days})
            tw = tw.sort_values('Days', ascending=True).reset_index(drop='index')
            if debug:
                return tw, weird
            else:
                return tw

    # Finds all students that need a 90 day CP
    def ndcp(self, comingup = False, debug=False):
        nom = []
        n_lc = []
        n_days = []
        for i in range(self.enrolled):
            n = self.sr['Student Name'][i]
            z = self.sr['Last Assessment'][i]
            w = z.split('/')
            # Calculates the number of days since last assessment
            if len(w) > 1 and n not in self.idle:
                day = w[0]
                month = w[1]
                last_date = date(2021, int(month), int(day))
                diff = self.today - last_date
                r = str(diff).split(' ')
                if debug:
                    print(r)
                # Checks if a student will need a ndcp within the next ten days
                if comingup and len(r) > 2 and 80 <= int(r[0]) < 90:
                    nom.append(n)
                    n_lc.append(z)
                    n_days.append(int(str(diff).split(' ')[0]))
                # Checks if the student needs a 90 day cp
                elif len(r) > 2 and int(r[0]) >= 90:
                    nom.append(n)
                    n_lc.append(z)
                    n_days.append(int(str(diff).split(' ')[0]))
        # Creating the DataFrames
        if len(nom) == 0:
            print('No Students')
        else:
            nd = pd.DataFrame({'Name': nom, 'Last Assessment': n_lc, 'Days': n_days})
            nd = nd.sort_values('Days', ascending=True).reset_index(drop='index')
            return nd

    # Finds the last time a student attended
    def student(self, name):
        nom = []
        nom_la = []
        n = name.split(' ')
        fn = n[0]
        for i in range(self.enrolled):
            u = self.sr['Student Name'][i]
            v = self.sr['Last Attendance'][i]
            if fn in u:
                nom.append(u)
                nom_la.append(v)
        ow = pd.DataFrame({'Name': nom, 'Last Attendance': nom_la})
        return ow

    # Searches the notes for keywords
    def note_search(self, keywords):
        notes = self.home[self.home['Notes'].isna() == False].reset_index(drop='index')
        name = []
        decks = []
        for i in range(len(notes)):
            nom = notes['Name'][i]
            # Checks if the note contains one of the keywords
            for k in keywords:
                if k in notes['Notes'][i]:
                    if nom not in name:
                        name.append(nom)
                        decks.append(notes['Notes'][i])
        df_note = pd.DataFrame({'Name': name, 'Notes': decks})
        return df_note

    # Checks if the athome sheet attendance matches the
    def check(self, debug=False):
        l = len(self.home['Name'])
        nom = []
        ah_att = []
        sr_att = []
        for i in range(l):
            name = self.home['Name'][i]
            fname = name.split(' ')[0]
            la = self.home['Date Updated'][i]
            att = Radius(self.sheet, self.athome).student(fname)
            for j in range(len(att['Name'])):
                x = att['Last Attendance'][j]
                # Checks for duplicate names
                if att['Name'][j] not in nom:
                    y = x[0].split('/')
                    z = str(la).split('-')
                    # Finds the difference between the two dates
                    if len(y) > 1 and len(z) > 1:
                        day1 = y[0]
                        month1 = y[1]
                        day2 = z[-1].split(' ')[0]
                        month2 = z[1]
                        last_date = date(2021, int(month1), int(day1))
                        curr_date = date(2021, int(month2), int(day2))
                        diff = curr_date - last_date
                        r = str(diff).split(' ')
                        if debug:
                            print('r:', r)
                        # Checks if there is a difference in the date
                        if int(r[0]) != 0:
                            nom.append(name)
                            ah_att.append(curr_date)
                            sr_att.append(last_date)
        # Creates the dataframe
        ath = pd.DataFrame({'Name': nom, 'AtHome Attendance': ah_att, 'SR Attendance': sr_att})
        return ath

    # Find's all the students that need to be checked for MPR
    def mpr(self, cbd, tol=1 / 3, htol= 1 / 4):
        df = pd.read_excel(str(cbd))
        data = df[['Student', 'Attendances', 'Skills Mastered']]
        l = len(data.Student)
        no_show = []
        check = []
        ch_att = []
        ch_sm = []
        rtio = []
        for i in range(l):
            nom = data.Student[i]
            fnom = nom.split(' ')[0]
            lnom = nom.split(' ')[1]
            # Filters students that have not attended this month
            if data.Attendances[i] == 0:
                no_show.append(data.Student[i])
            # Filters students that have attended less than three times
            elif data.Attendances[i] <= 3:
                ratio = data['Skills Mastered'][i] / data.Attendances[i]
                if ratio <= tol:
                    no_show.append(data.Student[i])
            else:
                ratio = data['Skills Mastered'][i] / data.Attendances[i]
                # Checks if the student is on athome
                if self.df['Delivery'][i] == "@home":
                    if ratio < htol:
                        check.append(data.Student[i])
                        ch_att.append(data.Attendances[i])
                        ch_sm.append(data['Skills Mastered'][i])
                        rtio.append(round(ratio, 2))
                elif ratio < tol:
                    check.append(data.Student[i])
                    ch_att.append(data.Attendances[i])
                    ch_sm.append(data['Skills Mastered'][i])
                    rtio.append(round(ratio, 2))
        dfns = pd.DataFrame({'Name': no_show})
        dfch = pd.DataFrame({'Name': check, 'Attendances': ch_att, 'Skills Mastered': ch_sm, 'Ratio': rtio})
        dfch = dfch.sort_values("Ratio", ascending=True).reset_index(drop='index')

        # Guesses why there is a low ratio
        notes = []
        for i in range(len(check)):
            n = dfch['Name'][i]
            m = ""
            # Checks if they are a GCSE Studednt
            if n.split(' ')[0] in ['Alex', 'Billy', 'Leo', 'Ozzy', 'Poppy', 'Shalini']:
                m += " GCSE student "
            for j in range(len(self.sr['Student Name'])):
                nn = self.sr['Student Name'][j]
                fnn = nn.split(' ')[0]
                lnn = nn.split(' ')[1]
                # Checks if they have recently done an assessment
                if nn == n:
                    pr = self.sr['Last Assessment'][j]
                    month = pr.split('/')[1]
                    if int(month) == 4:
                        if len(m) > 0:
                            m += ", Recent Assessment "
                        else:
                            m += n.split(' ')[0] + " Recent Assessment "
                # Checks if the student is on athome
                if n in self.df[self.df['Delivery'] == "@home"]['Student Name']:
                    if len(m) > 0:
                        m += ", on athome "
                    else:
                        m += n.split(' ')[0] + " on athome "
            # If there are no notes
            if len(m) == 0:
                m += n.split(' ')[0] + " Check LP "
            notes.append(m)
        dfch['Computer Guess'] = notes
        return dfns, dfch