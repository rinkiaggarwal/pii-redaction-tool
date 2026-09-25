import re
text = """
11/3, 11/4 and 11/5 19/29, Basak Street, Ahmedabad-328570
88/607, Swaminathan Road, Bangalore 821374 – 410 501
H.No. 20, Sahota Road, Bhavnagar 630078
92/648, Iyer, Salem-633451
00/31, Roy Ganj, Shimoga 264330
Tower 2, Salvi Ltd, Chopra Ltd, Adya Acharya – 411 29/32, Date, Katni 568512
"""
pattern = r'(?i)\b(?:[A-Z0-9][A-Za-z0-9\/\-\., ]{5,100}(?:Road|Street|Marg|Nagar|Colony|Ganj|Circle|Path|Zila|Bhavan|Estate|Park|Phase|Sector|Block|Apt|Building|Chowk)[A-Za-z0-9\/\-\., ]{1,50}\d{6})\b'
for match in re.finditer(pattern, text):
    print("Address:", match.group().strip())
