
def get_config_list(config, section, option):

    string = config.get(section, option)
    stringList = [sub.strip() for sub in string.split(',')]
    return stringList
