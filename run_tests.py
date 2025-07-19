#!/usr/bin/env python3

"""
Test runner script for Magisterium Client.

This script runs all unit and integration tests for the magisterium client.
It provides options for different verbosity levels and test selection.
"""

import sys
import unittest
import argparse


def run_tests(verbosity: int = 2, pattern: str = "test*.py") -> bool:
    """
    Run the test suite.
    
    Args:
        verbosity: Test output verbosity (0=quiet, 1=normal, 2=verbose)
        pattern: Test file pattern to match
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern=pattern)
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()


def main() -> None:
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests for Magisterium Client"
    )
    
    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Test output verbosity (0=quiet, 1=normal, 2=verbose)"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        default="test*.py",
        help="Test file pattern to match (default: test*.py)"
    )
    
    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (test_magisterium_client.py)"
    )
    
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests (test_integration.py)"
    )
    
    args = parser.parse_args()
    
    # Set pattern based on options
    pattern = args.pattern
    if args.unit_only:
        pattern = "test_magisterium_client.py"
    elif args.integration_only:
        pattern = "test_integration.py"
    
    print(f"Running tests with pattern: {pattern}")
    print("=" * 50)
    
    # Run tests
    success = run_tests(verbosity=args.verbosity, pattern=pattern)
    
    # Exit with appropriate code
    if success:
        print("\n" + "=" * 50)
        print("All tests passed! ✅")
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("Some tests failed! ❌")
        sys.exit(1)


if __name__ == "__main__":
    main()