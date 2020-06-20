
def string_to_list(string, separator=','):
    '''convert a string to a list of (stripped) strings, given a separator'''
    stringList = [sub.strip() for sub in string.split(separator)]
    return stringList
