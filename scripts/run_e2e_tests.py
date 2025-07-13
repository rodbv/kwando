#!/usr/bin/env python3
"""
Script to run E2E tests against the dashboard.
This script will:
1. Build the Docker image
2. Start the dashboard container
3. Run the E2E tests
4. Clean up the container
"""

import subprocess
import sys
import time


def run_command(command, check=True, capture_output=False):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(
        command, shell=True, check=check, capture_output=capture_output, text=True
    )
    return result


def main():
    """Main function to run E2E tests."""
    print("🚀 Starting E2E tests...")

    try:
        # Build Docker image
        print("\n📦 Building Docker image...")
        run_command("docker build -t kwando-dashboard .")

        # Start dashboard container
        print("\n🐳 Starting dashboard container...")
        run_command(
            "docker run -d --name kwando-e2e-test -p 5006:5006 kwando-dashboard"
        )

        # Wait for dashboard to start
        print("⏳ Waiting for dashboard to start...")
        time.sleep(15)

        # Check if container is running
        result = run_command(
            "docker ps --filter name=kwando-e2e-test --format '{{.Status}}'",
            capture_output=True,
        )
        if "Up" not in result.stdout:
            print("❌ Dashboard container failed to start")
            return 1

        print("✅ Dashboard is running")

        # Install Playwright if not already installed
        print("\n🔧 Installing Playwright...")
        run_command("pip install playwright pytest")
        run_command("playwright install chromium")

        # Run E2E tests
        print("\n🧪 Running E2E tests...")
        test_result = run_command("python -m pytest tests/e2e/ -v", check=False)

        if test_result.returncode == 0:
            print("\n✅ All E2E tests passed!")
        else:
            print("\n❌ Some E2E tests failed!")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during E2E test setup: {e}")
        return 1

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        run_command("docker stop kwando-e2e-test", check=False)
        run_command("docker rm kwando-e2e-test", check=False)

    return test_result.returncode if "test_result" in locals() else 0


if __name__ == "__main__":
    sys.exit(main())
