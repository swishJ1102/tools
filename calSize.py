import os

def count_lines_of_code(file_path):
    total_lines = 0
    total_code_lines = 0
    method_lines = {}
    method_code_lines = {}
    current_method_name = None
    current_method_lines = 0
    current_method_code_lines = 0
    brace_count = 0
    in_comment_block = False
    
    with open(file_path, 'r') as file:
        for line in file:
            # 去除行首尾空白字符
            line = line.strip()
            
            # 统计总行数
            total_lines += 1
            
            # 检查是否在注释块内
            if line.startswith("/*"):
                in_comment_block = True
            elif "*/" in line:
                in_comment_block = False
                
            # 检查是否进入了新方法
            if line.startswith("public") or line.startswith("private") or line.startswith("protected"):
                if current_method_name is not None:
                    method_lines[current_method_name] = current_method_lines
                    method_code_lines[current_method_name] = current_method_code_lines
                current_method_name = line.split("(")[0].split()[-1]
                current_method_lines = 0
                current_method_code_lines = 0
                brace_count = 0
                
            # 统计方法行数和纯代码行数
            if current_method_name is not None:
                if not line.startswith("//") and not in_comment_block and line != "":
                    current_method_lines += 1
                    total_code_lines += 1
                    current_method_code_lines += 1
                if "{" in line:
                    brace_count += 1
                if "}" in line:
                    brace_count -= 1
                    if brace_count == 0:
                        method_lines[current_method_name] = current_method_lines
                        method_code_lines[current_method_name] = current_method_code_lines
                        current_method_name = None
                        
    return total_lines, total_code_lines, method_lines, method_code_lines

def main():
    java_files = [file for file in os.listdir() if file.endswith(".java")]
    
    for java_file in java_files:
        total_lines, total_code_lines, method_lines, method_code_lines = count_lines_of_code(java_file)
        print(f"File: {java_file}")
        print(f"Total lines: {total_lines}")
        print(f"Total code lines: {total_code_lines}")
        print("Method lines:")
        for method, lines in method_lines.items():
            print(f"{method}: Total lines: {lines}, Code lines: {method_code_lines[method]}")
        print()

if __name__ == "__main__":
    main()