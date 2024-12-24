import sys
import unittest
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")

if __name__ == "__main__":
    unittest.main(
        module=None,
        defaultTest="discover",
        argv=[
            "",
            "discover",
            "-s",
            "tests",
            "-p",
            "test*.py",
            # "-v" # Verbose
        ]
    )
