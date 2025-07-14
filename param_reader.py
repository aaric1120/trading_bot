def param_reader (path: str):
    param_dict = {}
    try:
        with open(path, "r") as file:
            for line in file.readlines():
                values = line.split("=")
                param_dict[values[0].strip(" ")] = float(values[1].strip("\n").strip(" "))
    except Exception as e:
        print(e)
        raise Exception(e)

    return param_dict
