get_month = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}

get_league = {
    'LCK': '1',
    'LEC': '2',
    'LVP SuperLiga': '3',
    'LCO': '4',
    'LFL': '5',
    'PCS': '6',
    'LCS': '7',
    'NA Academy League': '8',
    'LLA': '9',
    'Ultraliga': '10',
    'LPL': '11',
    'LJL': '12',
    'TCL': '13',
    'VCS': '14',
    'CBLOL': '15',
    'LCK CL': '16',
    'LPLOL': '17',
    'NLC': '18',
    'Esports Balkan League': '19',
    'Hitpoint Masters': '20',
    'Prime League 1st Division': '21',
    'Turkey Academy League': '22',
    'Elite Series': '23',
}

get_split = {
    'LCK': '1',
    'LEC': '2',
    'LVP SuperLiga': '3',
    'LCO': '4',
    'LFL': '5',
    'PCS': '6',
    'LCS': '7',
    'NA Academy League': '8',
    'LLA': '9',
    'Ultraliga': '10',
    'LPL': '11',
    'LJL': '12',
    'TCL': '13',
    'VCS': '14',
    'CBLOL': '15',
    'LCK CL': '16',
    'LPLOL': '17',
    'NLC': '18',
    'Esports Balkan League': '19',
    'Hitpoint Masters': '20',
    'Prime League 1st Division': '21',
    'Turkey Academy League': '22',
    'Elite Series': '23',
}

def get_league_id(league):
    return get_league[league]

def get_split_id(league):
    return get_split[league]
