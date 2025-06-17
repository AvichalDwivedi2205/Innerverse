#!/usr/bin/env python3
"""Test runner script for Innerverse Agent System."""

import os
import sys
import subprocess
import argparse


def run_tests(test_type="all", coverage=True, verbose=True):
    """Run tests with specified configuration.
    
    Args:
        test_type: Type of tests to run ("all", "unit", "integration", "specific")
        coverage: Whether to run with coverage reporting
        verbose: Whether to run with verbose output
    """
    # Base pytest command
    cmd = ["python3", "-m", "pytest"]
    
    # Add test type filters
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=agents",
            "--cov-report=html", 
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ])
    
    # Add verbosity
    if verbose:
        cmd.append("--verbose")
    
    # Add async support
    cmd.append("--asyncio-mode=auto")
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run Innerverse Agent System tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run with minimal output"
    )
    parser.add_argument(
        "--file",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ.setdefault("ENVIRONMENT", "test")
    
    # If specific file requested, run it directly
    if args.file:
        cmd = ["python3", "-m", "pytest", args.file]
        if not args.no_coverage:
            cmd.extend(["--cov=agents"])
        if not args.quiet:
            cmd.append("--verbose")
        cmd.append("--asyncio-mode=auto")
        
        subprocess.run(cmd)
        return
    
    # Run tests with specified configuration
    success = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 