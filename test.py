import re 

pattern = r'\.\d{3,4}p\.'

stri = 'aquaman.and.the.lost.kingdom.2023.20p.uhd.bluray.x265-b0mbardiers.mkv'


x = re.search(pattern=pattern,string=stri)

# if x : 
print(x.group())


