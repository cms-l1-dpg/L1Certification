import webbrowser
import argparse
import importlib

parser = argparse.ArgumentParser()

parser.add_argument('--runs', type=str)
parser.add_argument('--refs', type=str)

args = parser.parse_args()

def url_search():

    url_base = 'https://cmsweb-testbed.cern.ch/dqm/autodqm/plots/Online/L1T_workspace_slim'

    run_list = args.runs.split(',') if ',' in args.runs else [args.runs]
    ref_list = args.refs.split(',') if ',' in args.refs else [args.refs]

    for run in run_list:
        run_str = '/'.join(['000'+run[:2]+'xxxx', '000'+run[:4]+'xx', run])

        for ref in ref_list:
            ref_str = '/'.join(['000'+ref[:2]+'xxxx', '000'+ref[:4]+'xx', ref])

            final_url = '/'.join([url_base, ref_str, run_str])
            print(final_url)
            #webbrowser.open(final_url)

### --------------------------------------------------------  ###

if __name__ == '__main__':
    url_search()

