import subprocess

test_cases = [
    {
        "description": "Basic acceptance for input 'aaaaa'",
        "input_string": "aaaaa",
        "max_depth": "10",
        "expected_result": "accept",
    },
    {
        "description": "Basic rejection for input 'bbbb'",
        "input_string": "bbbb",
        "max_depth": "10",
        "expected_result": "reject",
    },
    {
        "description": "Execution stops due to step limit with long input",
        "input_string": "aaaaaaaaaa",
        "max_depth": "5",
        "expected_result": "stopped",
    },
    {
        "description": "Single character acceptance",
        "input_string": "a",
        "max_depth": "10",
        "expected_result": "accept",
    },
    {
        "description": "Empty string rejection",
        "input_string": "",
        "max_depth": "10",
        "expected_result": "reject",
    },
    {
        "description": "Mixed invalid characters leading to rejection",
        "input_string": "ababa",
        "max_depth": "10",
        "expected_result": "reject",
    },
    {
        "description": "Large valid input string within depth limit",
        "input_string": "aaaaaaa",
        "max_depth": "15",
        "expected_result": "accept",
    },
    {
        "description": "Large valid input string exceeding depth limit",
        "input_string": "aaaaaaaaaa",
        "max_depth": "8",
        "expected_result": "stopped",
    },
]

traceNTM_path = "traceNTM_kwilli.py"
machine_file_path = "machine_kwilli.csv"

def run_test(case):
    result = subprocess.run(
        ["python3", traceNTM_path, machine_file_path, case["input_string"], case["max_depth"]],
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()

    if "String accepted in" in output:
        result_status = "accept"
    elif "String rejected in" in output:
        result_status = "reject"
    elif "Execution stopped after" in output:
        result_status = "stopped"
    else:
        result_status = "unknown"

    configurations_line = [line for line in output.split("\n") if "Total Configurations Explored:" in line]
    total_configurations = int(configurations_line[0].split(":")[-1]) if configurations_line else 0

    depth_line = [line for line in output.split("\n") if "Depth of Tree:" in line]
    depth = int(depth_line[0].split(":")[-1]) if depth_line else 0

    return {
        "input_string": case["input_string"],
        "result": result_status,
        "total_configurations": total_configurations,
        "depth": depth,
        "description": case["description"],
    }

def main():
    results = []
    for case in test_cases:
        test_result = run_test(case)
        results.append(test_result)

    print("-" * 100)
    print(f"{'Input String':<15} | {'Result':<8} | {'Configurations':<15} | {'Depth':<5} | {'Reason'}")
    print("-" * 100)
    for res in results:
        print(
            f"{res['input_string']:<15} | {res['result']:<8} | {res['total_configurations']:<15} | {res['depth']:<5} | {res['description']}"
        )
    print("-" * 100)

if __name__ == "__main__":
    main()
