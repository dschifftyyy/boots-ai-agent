from functions.get_files_info import get_files_info


def print_result(label, result):
    print(f"Result for {label}:")
    indent = "    " if result.startswith("Error:") else "  "
    for line in result.splitlines():
        print(indent + line)
    print()


def main():
    print_result("current directory", get_files_info("calculator", "."))
    print_result("'pkg' directory", get_files_info("calculator", "pkg"))
    print_result("'/bin' directory", get_files_info("calculator", "/bin"))
    print_result("'../' directory", get_files_info("calculator", "../"))


if __name__ == "__main__":
    main()
