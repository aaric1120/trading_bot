def param_reader (path: str):
    param_dict = {}
    with open(path, "r") as file:
        for line in file.readlines():
            values = line.split("=")
            param_dict[values[0]] = float(values[1].strip("\n"))

    return param_dict
