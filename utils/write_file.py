def write_file(filepath, content):
    f = open(filepath, "a")
    f.write(content + "\n")
