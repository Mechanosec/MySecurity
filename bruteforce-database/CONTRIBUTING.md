# Contributing to Bruteforce Database

Thank you for considering contributing to this project! This repository thrives because of community contributions like yours.

## Philosophy

Before contributing, please read [CLAUDE.md](./CLAUDE.md) to understand our principles:
- Quality over quantity
- Ethical use only
- Full transparency
- Community first

## How to Contribute

### Adding a New Wordlist

1. **Verify it's unique** - Check if we already have something similar
2. **Document the source** - Where did this come from? When? Why is it valuable?
3. **Ensure quality** - Run our validation tools before submitting
4. **Choose the right location** - Follow our directory structure

### Step-by-Step Process

#### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/bruteforce-database.git
cd bruteforce-database
```

#### 2. Create a Feature Branch

```bash
# Use a descriptive branch name
git checkout -b add-linkedin-passwords
```

#### 3. Add Your Wordlist

Place your file in the appropriate location:
```
passwords/          # For password dictionaries
usernames/          # For username lists
identities/         # For names, cities, etc.
infrastructure/     # For subdomains, directories, file paths
```

#### 4. Validate Your Contribution

```bash
# Install Python 3.8+ if not already installed

# Validate your specific file
python3 scripts/validate.py --file your-wordlist.txt

# Deduplicate if needed
python3 scripts/deduplicate.py your-wordlist.txt

# Run full validation suite
python3 scripts/validate.py
```

#### 5. Update Documentation

Add an entry to the README.md describing your wordlist:
```markdown
- **your-wordlist.txt**: Brief description of what it contains,
  source, and intended use case. Total: X entries.
```

#### 6. Commit with Clear Message

```bash
git add your-wordlist.txt README.md
git commit -m "feat: add LinkedIn passwords wordlist

- Source: LinkedIn breach dataset (2012)
- Entries: 123,456 unique passwords
- Use case: Testing common LinkedIn user passwords
- Validated and deduplicated"
```

#### 7. Push and Create Pull Request

```bash
git push origin add-linkedin-passwords
```

Then create a PR on GitHub with:
- Clear title describing what you're adding
- Description of the source and purpose
- Validation results (file size, entry count, etc.)

## Quality Standards

### File Format

- **Encoding:** UTF-8 (no BOM)
- **Line endings:** Unix (LF, not CRLF)
- **Format:** One entry per line
- **No empty lines** at the end
- **Sorted or deduplicated** preferred

### File Naming

- Use lowercase with hyphens: `common-passwords.txt`
- Include count if relevant: `10000-subdomains.txt`
- Describe the content: `facebook-firstnames.txt`
- Avoid version numbers in filename (use git history)

### Metadata Requirements

When adding a wordlist, document:
- **Source:** Where did this come from?
- **Date:** When was it collected/compiled?
- **Purpose:** What is it used for?
- **Count:** How many entries?
- **License:** Can it be redistributed?

### What We Accept

✅ **Good contributions:**
- Unique password dictionaries from verified breaches
- Username collections from public sources
- Specialized wordlists (keyboard patterns, years, etc.)
- Infrastructure lists (subdomains, directories, common files)
- Well-documented, deduplicated, and validated files

❌ **What we don't accept:**
- Duplicate of existing lists
- Poorly formatted or corrupted files
- Lists without clear source/provenance
- Potentially illegal or unethical content
- Personal information (PII) beyond usernames
- Lists with unclear licensing

## Testing

All contributions are automatically tested via GitHub Actions:

1. **Validation:** Files are checked for encoding, format, and integrity
2. **Security:** Scanned for sensitive data patterns
3. **Integrity:** Verified for corruption and consistency
4. **Statistics:** Entry counts and duplicates are calculated

You can run these checks locally:
```bash
# Full validation suite
python3 scripts/validate.py

# Generate manifest
python3 scripts/validate.py --manifest

# Deduplicate all files
python3 scripts/deduplicate.py --all
```

## Code of Conduct

### Ethical Use

This repository is for **authorized security testing only**:
- Penetration testing with proper authorization
- Security research and education
- Testing your own systems
- Academic research

**NOT for:**
- Unauthorized access to systems
- Malicious hacking or cybercrime
- Harassment or targeting individuals
- Any illegal activity

### Community Standards

- Be respectful and professional
- Provide constructive feedback
- Credit sources and contributors
- Help maintain quality standards
- Report issues and improvements

## Attribution

When contributing, you'll be added to:
- Git commit history (automatic)
- Contributors section in README
- Manifest metadata for your contributions

We use the following format:
```markdown
* Your Name - [**@username**](https://github.com/username)
```

## Questions?

- **General questions:** Open a Discussion on GitHub
- **Bug reports:** Open an Issue
- **Security concerns:** Email the maintainers directly
- **Contribution ideas:** Open an Issue to discuss first

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](./LICENSE) as the rest of the project.

This means:
- Your contributions are freely available
- Proper attribution is maintained
- No warranty or liability

## Recognition

We deeply appreciate every contribution:
- Your name in git history (forever)
- Listed in Contributors section
- Mentioned in release notes
- Karma in the security community ⭐

Thank you for making this resource better for everyone!

---

*"Alone we can do so little; together we can do so much." - Helen Keller*
