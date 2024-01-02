def format_telegram_message(string):
    for v in ['_', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        string = string.replace(v,f'\{v}')
    return string

def profit_convert(string):
    string = string.replace(',','')
    if string == '':
        return '-'
    if '(' in string:
        string = '-' + string.replace('(','').replace(')','')
    return int(string)