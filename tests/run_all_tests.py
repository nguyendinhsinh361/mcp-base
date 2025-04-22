import os
import asyncio
import argparse
import sys

# Add the parent directory to sys.path to allow importing from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test functions - use relative imports
from tests.test_combined import test_combined_servers

async def run_all_tests(selected_tests=None):
    """
    Run all or selected MCP server tests
    
    Args:
        selected_tests: List of test names to run. If None, run all tests.
    """
    # Define the available tests
    tests = {
        "combined": test_combined_servers
    }
    
    # Determine which tests to run
    tests_to_run = {}
    if selected_tests:
        for test_name in selected_tests:
            if test_name in tests:
                tests_to_run[test_name] = tests[test_name]
            else:
                print(f"❌ Warning: Unknown test '{test_name}'")
    else:
        # Run all tests if none specified
        tests_to_run = tests
    
    # Run the selected tests
    for name, test_func in tests_to_run.items():
        print(f"\n\n{'=' * 50}")
        print(f"Running {name.upper()} tests")
        print(f"{'=' * 50}\n")
        
        try:
            await test_func()
        except Exception as e:
            print(f"❌ Error running {name} tests: {e}")
    
    print(f"\n\n{'=' * 50}")
    print("All selected tests completed")
    print(f"{'=' * 50}\n")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run MCP server tests")
    parser.add_argument(
        "--tests", 
        nargs="+", 
        choices=["math", "weather", "github", "combined", "all"],
        help="Specify which tests to run (math, weather, github, combined, or all)"
    )
    
    args = parser.parse_args()
    
    # Handle the 'all' option
    selected_tests = None
    if args.tests and "all" not in args.tests:
        selected_tests = args.tests
    
    # Run the tests
    asyncio.run(run_all_tests(selected_tests))