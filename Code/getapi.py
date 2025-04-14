def ext_api(file_name: str)->dict[str, str]:
    api_dict = {}
    with open(file_name, 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            api_dict[key.strip()] = value.strip()
    return api_dict