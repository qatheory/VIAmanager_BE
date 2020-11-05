from datetime import date, datetime
today = date.today()

# dd/mm/YY
datestr = "2020-11-05T03:49:46+0000"
# chosenDate = date("2020-11-05T03:49:46+0000")
chosenDate = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S%z")
# try:
#     chosenDate = datetime.strptime(datestr, "%Y-%m-%d")
# except:
#     print("error")
d1 = chosenDate.strftime("%d%m%Y")
print("d1 =", d1)
