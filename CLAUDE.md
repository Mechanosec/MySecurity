# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Security research and tooling pet project. Current content focuses on PDF-based JavaScript injection techniques (e.g., embedding OpenAction JS payloads into PDFs using `pdfrw`).

## Structure

```
jsPdf/          # PDF manipulation / JS injection experiments
  main.py       # Embeds a JavaScript OpenAction into an existing PDF via pdfrw
```

## Dependencies

- `pdfrw` — Python library for reading/writing PDF files

Install: `pip install pdfrw`

## Running Scripts

```bash
# From project root or within jsPdf/
python jsPdf/main.py
```

Scripts expect input PDF files (e.g., `document.pdf`) to be present in the working directory. Output is written alongside the input (e.g., `tracked_document.pdf`).

## Context

This is a personal security research repo. Tools here are for authorized testing, CTF challenges, or educational exploration of attack techniques. New modules should follow the same pattern: self-contained scripts in a named subdirectory.
