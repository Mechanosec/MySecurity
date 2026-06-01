# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Automation & Quality Control**
  - Python validation tool (`scripts/validate.py`) for comprehensive wordlist validation
  - Deduplication tool (`scripts/deduplicate.py`) for removing duplicates
  - Real CI/CD pipeline with quality assurance checks
  - Manifest generation system for metadata tracking
  - Security scanning for sensitive data patterns
  - Integrity verification for file corruption detection

- **Documentation**
  - CLAUDE.md - Project philosophy and guiding principles
  - CONTRIBUTING.md - Comprehensive contribution guidelines
  - CHANGELOG.md - This file, tracking all changes
  - Enhanced README with usage examples and decision matrices

- **Infrastructure**
  - GitHub Actions workflows for automated validation
  - Metadata framework for tracking wordlist provenance
  - Statistics generation on every commit

### Changed
- **GitHub Actions**: Replaced placeholder "Hello, world!" workflow with meaningful validation suite
- **Quality Standards**: Established encoding, format, and validation requirements
- **Project Organization**: Defined clear directory structure and naming conventions

### Improved
- **Documentation**: Transformed from basic catalog to comprehensive guide
- **Validation**: Automated checks for encoding, duplicates, and integrity
- **Community**: Clear guidelines for ethical use and contribution

### Philosophy
This update represents a transformation from a **static archive** to a **living toolkit**. We're not just storing wordlists—we're curating them with intelligence, validating them automatically, and documenting them thoroughly.

---

## [1.0.0] - 2017-10-15

### Added
- Forced-browsing wordlists by @danivijay
  - Comprehensive directory/file discovery lists
  - Categorized by type (Conf, Database, Language, Project)
  - Contextual paths (admin, test, debug, error)
- Cain.txt password list (306,706 entries)

### Summary
Last major content update before entering maintenance mode. Established the core collection that has served the security community for years.

---

## [Historical] - 2015-2017

### Initial Collection (2015-2016)
- 2.1M password list from dazzlepod.com
- Facebook first names dataset (4.3M entries)
- Bitcoin brainwallet dictionary (394,748 words)
- US cities and usernames collections
- SecLists password compilation (1M entries)
- SKTorrent username and password lists
- Filtered password sets (7+ and 8+ character requirements)
- Indonesian cities list
- 10,000 common subdomains

### Contributors
Special thanks to all contributors who built this collection:
- Van-Duyet Le (@duyet) - Project creator and primary maintainer
- Taufiq Sumadi (@taufiqsumadi)
- San Sayidul Akdam Augusta (@sanAkdam)
- Dani Vijay (@danivijay) - Forced-browsing wordlists

---

## Future Roadmap

### Planned Improvements
- [ ] Reorganize directory structure for better navigation
- [ ] Add compressed versions (.gz) for large files
- [ ] Implement wordlist effectiveness metrics
- [ ] Create specialized subsets (top 100, top 1000, etc.)
- [ ] Add modern password patterns (passphrases, emoji passwords)
- [ ] Integrate with breach databases for automatic updates
- [ ] Build web interface for searching and filtering
- [ ] Create comparison matrices for choosing the right wordlist
- [ ] Add localized wordlists for non-English passwords

### Community Requests
Have a suggestion? [Open an issue](https://github.com/duyet/bruteforce-database/issues) or start a discussion!

---

## Versioning Strategy

We use semantic versioning:
- **MAJOR**: Significant reorganization or breaking changes
- **MINOR**: New wordlists or major improvements
- **PATCH**: Updates to existing wordlists or documentation

Current version reflects the **quality transformation**, not just content updates.

---

*"The only way to do great work is to love what you do." - Steve Jobs*
