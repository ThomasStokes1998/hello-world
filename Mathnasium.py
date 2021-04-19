import pandas as pd
from datetime import date

sheet=""

def attendance(name='att', file=sheet, debug=False, table=True):
    df = pd.read_excel(str(file))
    att = df[['First Name', 'Last Name', 'Last Attendance Date']]
    att = att.sort_values('Last Attendance Date', ascending=True).reset_index(drop='index')
    enrolled = len(att['First Name'])
    if name == 'att':
        today = date.today()
        one_week = []
        ow_index = []
        ow_la = []
        two_week = []
        tw_index = []
        tw_la = []
        tw_days = []
        weird = []
        w_index = []
        for i in range(enrolled):
            lad = att['Last Attendance Date']
            x = lad[i]
            y = x.split('/')
            if len(y) > 1:
                day = y[0]
                month = y[1]
                last_date = date(2021, int(month), int(day))
                diff = today - last_date
                r = str(diff).split(' ')
                if len(r) > 2:
                    if int(r[0]) >= 14:
                        two_week.append(att['First Name'][i] + ' ' + att['Last Name'][i])
                        tw_index.append(i)
                        tw_la.append(x)
                        tw_days.append(int(str(diff).split(' ')[0]))
                    elif 7 <= int(str(diff).split(' ')[0]) < 14:
                        one_week.append(att['First Name'][i] + ' ' + att['Last Name'][i])
                        ow_index.append(i)
                        ow_la.append(x)
            elif debug and len(y) <= 1:
                weird.append(att['First Name'][i] + ' ' + att['Last Name'][i])
                weird.append(x)
                w_index.append(i)
        if table:
            ow = pd.DataFrame({'Name': one_week, 'Last Attendance': ow_la})
            ow = ow.sort_values('Name', ascending=True).reset_index(drop='index')
            tw = pd.DataFrame({'Name': two_week, 'Last Attendance': tw_la, 'Days': tw_days})
            tw = tw.sort_values('Days', ascending=True).reset_index(drop='index')
            return ow, tw
        if debug:
            return one_week, two_week, weird
        else:
            return one_week, two_week
    else:
        n = name.split(' ')
        fn = n[0]
        data = att[att['First Name'] == fn].reset_index(drop='index')
        l = len(data['First Name'])
        if l == 0:
            return print('Invalid name.')
        if l == 1:
            return data
        if l > 1:
            if len(n) == 1:
                return data
            else:
                ln = n[1]
                for i in range(l):
                    x = data['Last Name'][i]
                    if x[0] == ln[0]:
                        return data[data['Last Name'] == x]
