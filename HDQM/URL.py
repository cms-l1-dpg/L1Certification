import webbrowser
import string
import numpy
import argparse
import os

#Establishing Option values
errors=1
fills=2
run_dur=4
binwid_prop_run=20
binwid_prop_del_lum=32
datetimeplt=68
regression=8
options = 0

#Making arguements for command lines                                                                                                                                                                   
 
#Creating Parser Argument                                                                                                                                                                              

parser = argparse.ArgumentParser(description = "A browser opening program")

#Tetsting Arguement                                                                                                                                                                                    

parser.add_argument("-s", dest='search', type=str, nargs = 3, metavar = ('plot_title', 'first_run', 'last_run'),
help = "Opens Browser for plots of title provided within range given.", default=None )
parser.add_argument('--int', required=False, help = "Prompts an interactive feature allowing for the direct input of each option for graphs.")
#parser.add_argument('--config', type=str, nargs = 1, required=False, metavar = ('pd'), help = "Input name of primary data set", default='SingleMuon')
#parser.add_argument('--ps', type=str, nargs = 1, required=False, metavar = ('ps'), help = "Not to be used ",default='PromptReco')
#parser.add_argument('--opt', type=int, nargs='*', metavar = ('options'), default = (0,0,0,0,0,0,0))
args = parser.parse_args()

def url_search():
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

    if args.search:
        user_input = {'subsys': 'L1T',
                      'plot_title': args.search[0],
                      'first_run': args.search[1],
                      'last_run': args.search[2],
                      'pd': 'SingleMuon',
                      'ps': 'PromptReco',
                      'opt': '3',}
        official_url=url+user_input['subsys']+pdurl+user_input['pd']+\
                      psurl+user_input['ps']+rangeurl+user_input['first_run']+comma+\
                      user_input['last_run']+optionurl+user_input['opt']+"&"+\
                      user_input['plot_title']
        print(official_url)
        #webbrowser.open(official_url)
    if args.int:
        user_input = get_input()
        official_url=url+user_input['subsys']+pdurl+user_input['pd']+\
                      psurl+user_input['ps']+rangeurl+user_input['first_run']+comma+\
                      user_input['last_run']+optionurl+user_input['opt']+"&"+\
                      user_input['plot_title']
        print(official_url)
        #webbrowser.open(official_url)

def get_input():
    options = 0
    #Obtaining information used for plot strings
    subsys = input("Enter your subsystem: ")
    pd = input("Enter your pd: ")
    ps = input("Enter your ps: ")
    first_run = input("Enter the first run number: ")
    last_run = input("Enter the final run number at the end of desired range: ")
    plot_title = input("Enter plot title: ")

    output_dict = {'subsys':subsys, 'pd':pd, 'ps':ps, 'first_run':first_run, 'last_run':last_run, 'plot_title':plot_title}
    
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
    #print(options)
    output_dict['opt'] = str(options)
    #print(optionurl + opt)
    return output_dict


if __name__ == '__main__':
    url_search()
