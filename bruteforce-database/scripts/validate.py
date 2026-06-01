#!/usr/bin/env python3
"""
Wordlist Validation and Quality Control System

This tool validates wordlist files for:
- Encoding consistency (UTF-8)
- Format correctness (one entry per line)
- File integrity (no corruption)
- Basic statistics generation

Philosophy: Quality is not an act, it's a habit.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class WordlistValidator:
    """Validates and analyzes wordlist files with surgical precision."""

    def __init__(self, root_dir: Path = None):
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.errors = []
        self.warnings = []

    def validate_file(self, filepath: Path) -> Dict:
        """
        Validate a single wordlist file.

        Returns comprehensive metadata and validation results.
        """
        if not filepath.exists():
            return {"error": "File does not exist"}

        result = {
            "path": str(filepath.relative_to(self.root_dir)),
            "size_bytes": filepath.stat().st_size,
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        try:
            # Detect encoding
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result["sha256"] = hashlib.sha256(raw_data).hexdigest()

            # Try UTF-8 first
            try:
                content = raw_data.decode('utf-8')
                result["encoding"] = "utf-8"
            except UnicodeDecodeError:
                try:
                    content = raw_data.decode('latin-1')
                    result["encoding"] = "latin-1"
                    result["warnings"].append("Non-UTF-8 encoding detected")
                except Exception as e:
                    result["valid"] = False
                    result["errors"].append(f"Encoding error: {e}")
                    return result

            # Analyze content
            lines = content.splitlines()
            result["total_lines"] = len(lines)

            # Filter empty lines
            non_empty_lines = [line for line in lines if line.strip()]
            result["non_empty_lines"] = len(non_empty_lines)

            # Check for duplicates
            unique_entries = set(non_empty_lines)
            result["unique_entries"] = len(unique_entries)

            if len(unique_entries) < len(non_empty_lines):
                duplicates = len(non_empty_lines) - len(unique_entries)
                result["warnings"].append(f"{duplicates} duplicate entries found")
                result["duplicate_count"] = duplicates

            # Line length statistics
            if non_empty_lines:
                lengths = [len(line) for line in non_empty_lines]
                result["min_length"] = min(lengths)
                result["max_length"] = max(lengths)
                result["avg_length"] = sum(lengths) / len(lengths)

            # Check for binary content
            if any(ord(c) < 32 and c not in '\t\n\r' for line in lines[:100] for c in line):
                result["warnings"].append("Possible binary content detected")

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {e}")

        return result

    def find_wordlists(self) -> List[Path]:
        """Find all wordlist files (*.txt, *.lst) in the repository."""
        wordlists = []

        # Skip certain directories
        skip_dirs = {'.git', 'node_modules', 'scripts', '__pycache__'}

        for txt_file in self.root_dir.rglob('*.txt'):
            if not any(skip in txt_file.parts for skip in skip_dirs):
                wordlists.append(txt_file)

        for lst_file in self.root_dir.rglob('*.lst'):
            if not any(skip in lst_file.parts for skip in skip_dirs):
                wordlists.append(lst_file)

        return sorted(wordlists)

    def validate_all(self) -> Dict:
        """Validate all wordlists and generate comprehensive report."""
        wordlists = self.find_wordlists()

        results = {
            "validation_date": "2025-11-16",
            "total_files": len(wordlists),
            "files": [],
            "summary": {
                "valid_files": 0,
                "invalid_files": 0,
                "total_warnings": 0,
                "total_size_bytes": 0,
                "total_entries": 0,
                "total_unique_entries": 0,
            }
        }

        print(f"🔍 Validating {len(wordlists)} wordlist files...\n")

        for wordlist in wordlists:
            print(f"  Checking {wordlist.name}...", end=" ")
            file_result = self.validate_file(wordlist)
            results["files"].append(file_result)

            if file_result["valid"]:
                results["summary"]["valid_files"] += 1
                print("✓")
            else:
                results["summary"]["invalid_files"] += 1
                print("✗")

            results["summary"]["total_warnings"] += len(file_result.get("warnings", []))
            results["summary"]["total_size_bytes"] += file_result.get("size_bytes", 0)
            results["summary"]["total_entries"] += file_result.get("non_empty_lines", 0)
            results["summary"]["total_unique_entries"] += file_result.get("unique_entries", 0)

        return results

    def generate_manifest(self, output_path: Path = None):
        """Generate a comprehensive manifest of all wordlists."""
        output_path = output_path or self.root_dir / "manifest.json"

        results = self.validate_all()

        # Pretty print summary
        summary = results["summary"]
        print(f"\n📊 Validation Summary:")
        print(f"  Total files: {results['total_files']}")
        print(f"  Valid: {summary['valid_files']} ✓")
        print(f"  Invalid: {summary['invalid_files']} ✗")
        print(f"  Warnings: {summary['total_warnings']}")
        print(f"  Total size: {summary['total_size_bytes'] / 1024 / 1024:.2f} MB")
        print(f"  Total entries: {summary['total_entries']:,}")
        print(f"  Unique entries: {summary['total_unique_entries']:,}")

        # Save manifest
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Manifest saved to {output_path}")

        # Return exit code based on validation
        return 0 if summary['invalid_files'] == 0 else 1


def main():
    """Main entry point for validation tool."""
    validator = WordlistValidator()

    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        # Validate single file
        filepath = Path(sys.argv[2])
        result = validator.validate_file(filepath)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)
    else:
        # Validate all and generate manifest
        sys.exit(validator.generate_manifest())


if __name__ == "__main__":
    main()
