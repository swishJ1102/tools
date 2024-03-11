import os

def count_lines_of_code(file_path):
    total_lines = 0
    method_lines = {}
    current_method_name = None
    current_method_lines = 0
    brace_count = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            # 统计总行数
            total_lines += 1
            
            # 检查是否进入了新方法
            if line.strip().startswith("public") or line.strip().startswith("private") or line.strip().startswith("protected"):
                current_method_name = line.split("(")[0].split()[-1]
                current_method_lines = 0
                brace_count = 0
                
            # 统计方法行数
            if current_method_name is not None:
                current_method_lines += 1
                if "{" in line:
                    brace_count += 1
                if "}" in line:
                    brace_count -= 1
                    if brace_count == 0:
                        method_lines[current_method_name] = current_method_lines
                        current_method_name = None
                    
    return total_lines, method_lines

def main():
    java_files = [file for file in os.listdir() if file.endswith(".java")]
    
    for java_file in java_files:
        total_lines, method_lines = count_lines_of_code(java_file)
        print(f"File: {java_file}")
        print(f"Total lines: {total_lines}")
        print("Method lines:")
        for method, lines in method_lines.items():
            print(f"{method}: {lines}")
        print()

if __name__ == "__main__":
    main()