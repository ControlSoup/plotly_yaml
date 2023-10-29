#!/user/bin/python

from plotly import graph_objects as go
import argparse
import os
import pandas as pd
from yaml import load
import sys
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def parse_args():
    parser = argparse.ArgumentParser(
        prog="plot_yaml",
        description="plotly from a yaml config"
    )
    parser.add_argument(
        "-i","--input",
        help="File path to your input yaml"
    )
    parser.add_argument(
        "-o","--output",
        help="File path to save your plot"
    )
    return parser.parse_args()


def csv_to_datadict(file_path: str):
    df = pd.read_csv(file_path)
    datadict ={}
    for key in df:
        datadict[key] = df[key].to_numpy()
    return datadict

def plot_from_yaml(group_name: str, plot_list: list, datadict: dict):

    for plot_name, plot_contents in plot_list.items():
        fig = go.Figure()

        # Required Args
        x_key = plot_contents['x_key']
        key_list = plot_contents['key_list']

        # Defaults
        if 'type' not in plot_contents:
            type = 'Line'
        else:
            type = plot_contents['type']

        if 'ylabel' not in plot_name:
            ylabel = ''

        # Errors
        if x_key not in datadict:
            print(f'    ERROR| x_key "{x_key}" not in csv file')
            exit(1)

        if type == 'Line':
            for key in key_list:

                if key not in datadict:
                    print(f'    ERROR| key "{key}" not in csv file')
                    exit(1)

                fig.add_trace(
                    go.Scatter(
                        x=datadict[x_key],
                        y=datadict[key],
                        name=key
                    )
                )
        fig.update_layout(
            title_text=f'{group_name} - {plot_name}',
            xaxis_title=x_key,
            yaxis_title=ylabel,
            showlegend=True
        )
        fig.show()

def main():

    abs_path = os.getcwd()

    args = parse_args()
    if args.input:
        yaml_path = os.path.join(abs_path, args.input)
        yaml_dir = os.path.dirname(yaml_path)
    else:
        print(f"    ERROR| Please use -i for yaml config path")
        sys.exit(1)

    # Parse Yaml
    yaml = open(yaml_path, 'r')
    yaml_dict = load(yaml)

    # Globals
    DATA_PATH_KEY = "DataPath"
    PLOT_NAME_KEY = "Name"
    PLOT_LIST_KEY = "Plots"

    # Check Errors
    if DATA_PATH_KEY in yaml_dict:
        data_path = yaml_dict[DATA_PATH_KEY]
        path = os.path.join(yaml_dir, data_path)
        datadict = csv_to_datadict(path)
    else:
        print(f'    ERROR| "{DATA_PATH_KEY}" field not found in yaml')
        exit(1)

    if PLOT_NAME_KEY in yaml_dict:
        group_name = yaml_dict[PLOT_NAME_KEY]
    else:
        print(f'    ERROR| "{PLOT_NAME_KEY}" field not found in yaml')
        exit(1)

    if PLOT_LIST_KEY in yaml_dict:
        plot_dict = yaml_dict[PLOT_LIST_KEY]
    else:
        print(f'    ERROR| "{PLOT_LIST_KEY}" field not found in yaml')
        exit(1)

    # Plot the files
    plot_from_yaml(group_name, plot_dict, datadict)

if __name__ == '__main__':
    main()