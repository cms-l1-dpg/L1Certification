import webbrowser
import string
import numpy

#initializing url text that is always apparent
url = "https://cms-hdqm.web.cern.ch/?subsystem="
pdurl = "&pd="
psurl = "&ps="
rangeurl = "&filter=range&filterValue="
comma = "%2C"
optionurl = "&options="
tsearchurl = "&search="

#initializing each interger value for options
#int errors
#int fills
#int run_dur
#int binwid_prop_run
#int binwid_prop_del_lum
#int datetimeplt
#int regression
#int options
errors=1
fills=2
run_dur=4
binwid_prop_run=20
binwid_prop_del_lum=32
datetimeplt=68
regression=8
options=0
check="0"

#Obtaining information used for plot strings
subsys = input("Enter your subsystem: ")
pd = input("Enter your pd: ")
ps = input("Enter your ps: ")
first_run = input("Enter the first run number: ")
last_run = input("Enter the final run number at the end of desired range: ")
plot_title = input("Enter plot title: ")

#Allowing for more accessible Yes,yes,Y,y,1 and No,no,N,n,0
cond1 = ["1","Yes","yes","Y","y"]
cond2 = ["0","No","no","N","n"]

#Obtaining the values of option
print("For the following questions respond 1 for yes, 0 for no.")

check = input("Do you wish to show errors on your plots?: ")
#print(check, check==1)
#exit()
if check in cond1:
    options = options + errors
    #print(options)
#    check = 0
#exit()     
check = input("Do you wish to show fill on your plots?: ")
if check in cond1:
    options = options + fills
#    check = 0

check = input("Do you wish to show run durations on your plots?: ")
if check in cond1:
    options = options + run_dur
#    check = 0

check = input("Do you wish to set bin width to be proportional to run duration on your plots?: ")
if check in cond1:
    options = options + binwid_prop_run
#    check = 0

check = input("Do you wish to set bin width to be proportional to delivered luminosity on your plots?: ")
if check in cond1:
    options = options + binwid_prop_del_lum
#    check = 0

check = input("Do you wish to show date time plots?: ")
if check in cond1:
    options = options + datetimeplt
#    check = 0

check = input("Do you wish to show regression lines on your plots?: ")
if check in cond1:
    options = options + regression
#    check = 0

#print(check) 
print(options)
opt = str(options)
#print(optionurl + opt)

#official_url=url+subsys+pdurl+pd+psurl+ps+rangeurl+first_run+comma+last_run+optionurl+opt+"&"+plot_title
#print(official_url)
#webbrowser.open(official_url)

