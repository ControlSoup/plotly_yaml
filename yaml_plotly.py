#!/usr/bin/python

import argparse
import os
import pandas as pd
from plotly import graph_objects as go
import sys
from yaml import load
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


def figs_from_yaml(
    group_name: str,
    plot_list: list,
    datadict: dict
) -> list[(str, go.Figure)]:

    fig_list = []

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
        else:
            print(
                f'    ERROR| type field "{type}" it not supported please use:'
                + '           [Line]'
            )
            exit(1)

        fig_title = f'{group_name}-{plot_name}'
        fig.update_layout(
            title_text=fig_title,
            xaxis_title=x_key,
            yaxis_title=ylabel,
            showlegend=True
        )
        fig_list.append((fig_title, fig))

    return fig_list

def output_fig_list(fig_list: list[(str, go.Figure)], output_path = None):
    for tuple in fig_list:
        name, fig = tuple

        if output_path is None:
            fig.show()
        else:
            fig.write_html(os.path.join(output_path, name + '.html'))


def main():

    abs_path = os.getcwd()

    args = parse_args()

    if not args.input:
        print(f"    ERROR| Please use -i for yaml config path")
        sys.exit(1)
    yaml_path = os.path.join(abs_path, args.input)
    yaml_dir = os.path.dirname(yaml_path)

    output_path = None
    if args.output:

        if args.output == '.' or '' or 'current':
            output_path = yaml_dir
        else:
            output_path = os.join(abs_path, args.output)


    # Parse Yaml
    yaml = open(yaml_path, 'r')
    yaml_dict = load(yaml, Loader=Loader)

    # Globals
    DATA_PATH_KEY = "DataPath"
    PLOT_NAME_KEY = "Name"
    PLOT_LIST_KEY = "Plots"

    # Check Errors
    if not DATA_PATH_KEY in yaml_dict:
        print(f'    ERROR| "{DATA_PATH_KEY}" field not found in yaml')
        exit(1)

    if not PLOT_NAME_KEY in yaml_dict:
        print(f'    ERROR| "{PLOT_NAME_KEY}" field not found in yaml')
        exit(1)

    if not PLOT_LIST_KEY in yaml_dict:
        print(f'    ERROR| "{PLOT_LIST_KEY}" field not found in yaml')
        exit(1)

    # Parse inputs
    data_path = yaml_dict[DATA_PATH_KEY]
    path = os.path.join(yaml_dir, data_path)
    datadict = csv_to_datadict(path)

    group_name = yaml_dict[PLOT_NAME_KEY]
    plot_dict = yaml_dict[PLOT_LIST_KEY]

    # Plot the files
    fig_list = figs_from_yaml(group_name, plot_dict, datadict)

    # Output
    output_fig_list(fig_list, output_path)

if __name__ == '__main__':
    main()