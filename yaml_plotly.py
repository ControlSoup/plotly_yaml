#!/usr/bin/python

import argparse
import os
import pandas as pd
import numpy as np
from plotly import graph_objects as go
import sys
import re
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


def plotly_list_from_datadict(
    datadict: dict[str, np.array],
    x_key: str,
    key_list: list[str],
    fig: go.Figure,
    mode: str = 'line',
    title: str = '',
    yaxis_number = None
):
    for key in key_list:

        if yaxis_number is None or yaxis_number == 0:
            y_str = 'y'
        else:
            y_str = f'y{yaxis_number}'
            print(y_str)

        fig.add_trace(
            go.Scatter(
                mode=mode,
                x=datadict[x_key],
                y=datadict[key],
                name=key,
                yaxis=y_str
            )
        )
        fig.update_layout(
            title_text=title,
            xaxis_title=x_key,
            showlegend=True
        )


def parse_axis(
    plot_contents: dict[str, str]
):
    pattern = r'^axis\d+$'
    axis_list = []

    for key in plot_contents:
        if re.match(pattern, key):
            axis_list.append(plot_contents[key])

    if len(axis_list) > 8:
        print('    ERROR| Cannot plot more than 8 axis')

    return axis_list


def get_axis_properties(
    axis_properties: dict[str, str],
    group_name: str,
    plot_name: str,
    x_key: str,
    datadict: dict[str, np.array]
):


    if 'mode' not in axis_properties:
        mode = 'lines'
    else:
        mode = axis_properties['mode']

    if 'y_label' not in axis_properties:
        y_label = ''
    else:
        y_label = axis_properties['y_label']

    if group_name != ('' or ' '):
        fig_title = f'{group_name}-{plot_name}'
    else:
        fig_title = plot_name


    if plot_name == 'All':
        key_list = [key for key in datadict if key != x_key]

    elif 'key_list' not in axis_properties:
        print(f'    ERROR| "key_list" not in {plot_name}')
        sys.exit(1)

    else:
        key_list = axis_properties['key_list']

    return [mode, y_label, fig_title, key_list]


def figs_from_yaml(
    group_name: str,
    plot_list: list,
    datadict: dict[str, np.array]
) -> list[(str, go.Figure)]:

    fig_list = []


    for plot_name, plot_contents in plot_list.items():
        fig = go.Figure()

        x_key = plot_contents['x_key']

        # Errors
        if x_key not in datadict:
            print(f'    ERROR| x_key "{x_key}" not in csv file')
            exit(1)

        axis_list = parse_axis(plot_contents)

        if len(axis_list):

            # Create the figure
            fig = go.Figure()
            for i, axis_properties in enumerate(axis_list):
                mode, y_label, fig_title, key_list = get_axis_properties(
                    axis_properties,
                    group_name,
                    plot_name,
                    x_key,
                    datadict
                )

                axis = go.layout.YAxis(
                    title=y_label,
                    anchor="free",
                    overlaying="y",
                    autoshift=True
                )

                # Support up to 8 axis
                match i:
                    case 0:
                        fig.update_layout(
                            yaxis= dict(title=y_label)
                        )
                    case 1:
                        fig.update_layout(
                            yaxis2 = axis
                        )
                    case 2:
                        fig.update_layout(
                            yaxis3 = axis
                        )
                    case 3:
                        fig.update_layout(
                            yaxis4 = axis
                        )
                    case 4:
                        fig.update_layout(
                            yaxis5 = axis
                        )
                    case 5:
                        fig.update_layout(
                            yaxis6 = axis
                        )
                    case 6:
                        fig.update_layout(
                            yaxis7 = axis
                        )
                    case 7:
                        fig.update_layout(
                            yaxis8 = axis
                        )

                plotly_list_from_datadict(
                    datadict,
                    x_key,
                    key_list,
                    fig,
                    mode,
                    fig_title,
                    yaxis_number=i+1
                )

            fig_list.append((fig_title, fig))

        else:
            print(plot_name, axis_list)
            mode, y_label, fig_title, key_list = get_axis_properties(
                plot_contents,
                group_name,
                plot_name,
                x_key,
                datadict
            )

            # Create the figure
            fig = go.Figure()
            plotly_list_from_datadict(
                datadict,
                x_key,
                key_list,
                fig,
                mode,
                fig_title
            )
            fig.update_layout(
                yaxis_title=y_label,
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
    GROUP_NAME_KEY = "GroupName"
    PLOT_LIST_KEY = "Plots"

    # Check Errors
    if not DATA_PATH_KEY in yaml_dict:
        print(f'    ERROR| "{DATA_PATH_KEY}" field not found in yaml')
        exit(1)

    if not GROUP_NAME_KEY in yaml_dict:
        group_name = ''
    else:
        group_name = yaml_dict[GROUP_NAME_KEY]

    if not PLOT_LIST_KEY in yaml_dict:
        print(f'    ERROR| "{PLOT_LIST_KEY}" field not found in yaml')
        exit(1)

    # Parse inputs
    data_path = yaml_dict[DATA_PATH_KEY]
    path = os.path.join(yaml_dir, data_path)
    datadict = csv_to_datadict(path)

    plot_dict = yaml_dict[PLOT_LIST_KEY]

    # Plot the files
    fig_list = figs_from_yaml(group_name, plot_dict, datadict)

    # Output
    output_fig_list(fig_list, output_path)

if __name__ == '__main__':
    main()