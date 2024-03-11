import re

def count_method_lines(file_path, method_name):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    total_method_lines = 0
    code_lines = 0
    in_method = False
    
    for line in lines:
        # Remove single line comments
        line = re.sub(r'//.*', '', line)
        
        # Remove multi-line comments
        line = re.sub(r'/\*.*?\*/', '', line)
        
        if in_method:
            total_method_lines += 1
            if line.strip() and not re.match(r'\s*//', line) and not re.match(r'\s*/\*', line) and not re.match(r'\s*\*', line):  # Exclude empty lines and comment lines
                code_lines += 1
        
        if re.match(r'.*\s*{}\(.*\)'.format(method_name), line):
            in_method = True
        elif in_method and re.match(r'\s*}}\s*', line):
            in_method = False
    
    return total_method_lines, code_lines

file_path = 'YourJavaFile.java'
method_name = 'yourMethodName'

total_method_lines, code_lines = count_method_lines(file_path, method_name)
print("Total lines in method '{}': {}".format(method_name, total_method_lines))
print("Number of non-empty lines in method '{}' (excluding comments and empty lines): {}".format(method_name, code_lines))