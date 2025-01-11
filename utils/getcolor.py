import pandas as pd

# Reading CSV file with pandas and giving names to each column
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# function to calculate minimum distance from all colors and get the most matching color
def get_color_name(param_red, param_green, param_blue):
    minimum = 10000
    color_name = ""
    for i in range(len(csv)):
        d = abs(param_red - int(csv.loc[i, "R"])) + abs(param_green - int(csv.loc[i, "G"])) + abs(
            param_blue - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            color_name = csv.loc[i, "color_name"]
    return color_name
