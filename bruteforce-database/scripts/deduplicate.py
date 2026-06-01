#!/usr/bin/env python3
"""
Wordlist Deduplication Tool

Remove duplicate entries from wordlists while preserving order and quality.

Philosophy: Perfection is achieved not when there is nothing more to add,
but when there is nothing left to take away.
"""

import sys
from pathlib import Path
from typing import Set, List


def deduplicate_file(filepath: Path, output_path: Path = None, preserve_order: bool = True):
    """
    Remove duplicates from a wordlist file.

    Args:
        filepath: Input wordlist file
        output_path: Output file (overwrites input if None)
        preserve_order: Keep first occurrence order (slower but maintains context)
    """
    print(f"📋 Processing {filepath.name}...")

    # Read file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    original_count = len(lines)
    print(f"  Original: {original_count:,} lines")

    # Deduplicate
    if preserve_order:
        seen: Set[str] = set()
        unique_lines: List[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_lines.append(stripped + '\n')
    else:
        # Faster but changes order
        unique_lines = sorted(set(line.strip() for line in lines if line.strip()))
        unique_lines = [line + '\n' for line in unique_lines]

    unique_count = len(unique_lines)
    removed = original_count - unique_count

    print(f"  Unique: {unique_count:,} lines")
    print(f"  Removed: {removed:,} duplicates ({removed/original_count*100:.1f}%)")

    # Write output
    output = output_path or filepath
    with open(output, 'w', encoding='utf-8') as f:
        f.writelines(unique_lines)

    print(f"  ✓ Saved to {output.name}\n")

    return {
        "original": original_count,
        "unique": unique_count,
        "removed": removed,
        "percentage": removed/original_count*100 if original_count > 0 else 0
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: deduplicate.py <wordlist.txt> [output.txt]")
        print("       deduplicate.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Deduplicate all wordlists in place
        root = Path(__file__).parent.parent
        wordlists = list(root.glob('*.txt')) + list(root.glob('*.lst'))

        print(f"🔄 Deduplicating {len(wordlists)} wordlists...\n")

        total_removed = 0
        for wordlist in sorted(wordlists):
            result = deduplicate_file(wordlist)
            total_removed += result["removed"]

        print(f"✨ Complete! Removed {total_removed:,} total duplicates.")
    else:
        # Deduplicate single file
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        deduplicate_file(input_file, output_file)


if __name__ == "__main__":
    main()
