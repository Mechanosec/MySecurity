# Validation & Quality Control Scripts

This directory contains tools for maintaining the quality and integrity of the wordlist collection.

## Scripts

### `validate.py`
Validates all wordlists and generates a comprehensive manifest.

**Features:**
- Encoding detection and validation
- Duplicate detection
- File integrity checks (SHA256)
- Statistics generation (line counts, lengths, etc.)
- Manifest generation with full metadata

**Usage:**
```bash
# Validate all wordlists and generate manifest
python3 validate.py

# Validate a specific file
python3 validate.py --file wordlist.txt
```

**Output:**
- Console output showing validation progress
- `manifest.json` with comprehensive metadata
- Exit code 0 if all files valid, 1 if any invalid

### `deduplicate.py`
Remove duplicate entries from wordlists while preserving order.

**Features:**
- Order-preserving deduplication (keeps first occurrence)
- Batch processing of all wordlists
- Statistics reporting (duplicates removed, percentage)

**Usage:**
```bash
# Deduplicate a specific file
python3 deduplicate.py wordlist.txt

# Deduplicate with output to new file
python3 deduplicate.py input.txt output.txt

# Deduplicate all wordlists in place
python3 deduplicate.py --all
```

**Note:** Use `--all` with caution as it modifies files in place.

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## CI/CD Integration

These scripts are automatically run by GitHub Actions on every commit and pull request.

See [`.github/workflows/validate.yml`](../.github/workflows/validate.yml) for the CI/CD configuration.

## Philosophy

These tools embody our commitment to quality:
- **Automation over manual effort** - Quality checks should be automatic
- **Transparency through data** - Every file's metadata is tracked
- **Prevention over correction** - Catch issues before they reach users
- **Simplicity in implementation** - Readable code that anyone can understand

---

**"Quality is not an act, it's a habit." - Aristotle**
