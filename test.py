import re 

# pattern = r'\.\d{3,4}p\.'
pattern = r'S0?1E0?13'
stri = 'aquaman.and.the.lost.kingdom.2023.20p.uhd.bluray.x265-b0mbardiers.mkv'
# print(stri[-2:])

string = 'La.casa.de.papel.S01E13.SPA-ENG.1080p.10bit.WEBRip.2CH.x265.HEVC-PSA.mkv' 
x = re.search(pattern=pattern,string=string)
print(x)
if x : 
    print(x.group())

# if int(' 01   ') == 1 : 
#     print('wtf')