def param_reader (path: str):
    param_dict = {}
    with open(path, "r") as file:
        for line in file.readlines():
            values = line.split("=")
            param_dict[values[0].strip(" ")] = float(values[1].strip("\n").strip(" "))

    return param_dict
