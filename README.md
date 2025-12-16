# Detecting Inconsistencies in ARM CCA’s Formally Verified Specification (ASPLOS 2026)

### [Paper](TBD)

A sophisticated Python tool that converts ARM CCA's Realm Management Monitor (RMM) specification documents into Verus verification code for formal analysis.

## What is the scope?

The `scope` is a shorthand for `spectroscope`. The name reflects the way a spectroscope takes incoming light (spec) and shines it through a prism. 

## Features

- **Multi-Specification Support**: Supports EAC5, REL0, and ALP11-ALP14 specifications
- **Flexible Input Processing**: Handles both PDF and text input files
- **Multiple Processing Modes**: Reasoning, rule-based checking, and raw parsing modes
- **Formal Verification**: Generates Verus code for verification

## Installation

### Prerequisites

```bash
# Install Python dependencies (if any)
# The scope uses only standard library modules

# Install PDF processing dependencies
sudo apt-get install poppler-utils

# For development (optional)
sudo apt-get install libpoppler-dev
```

### Quick Start

```bash
# Make the scope executable
chmod +x scope

# Run with default settings (EAC5 text file, reasoning mode)
./scope

# Process a PDF file directly
./scope --input-type pdf --target eac5

# Use rule-based checking mode
./scope --mode rule --target alp14

# Process with custom settings
./scope --target rel0 --mode reason --input-type pdf
```

## Usage

### Command Line Options

- `--target`: Specify target specification (eac5, rel0, alp11, alp12, alp13, alp14)
- `--mode`: Processing mode (reason, rule, raw)
- `--input-type`: Input file type (pdf, txt)

### Processing Modes

1. **Reasoning Mode** (`--mode reason`): Full conversion to Verus verification code
2. **Rule-based check Mode** (`--mode rule`): Analysis and validation without conversion
3. **Raw Mode** (`--mode raw`): Document parsing without processing

### Input Types

1. **Text Input** (`--input-type txt`): Process pre-converted text files
2. **PDF Input** (`--input-type pdf`): Automatically convert PDF to text

## Examples

### Basic Usage

```bash
# Process EAC5 specification (default)
./scope

# Process ALP14 specification with text input
./scope --target alp14 --input-type txt

# Process REL0 specification with PDF input
./scope --target rel0 --input-type pdf

# Generate only RMM model without processing dependency tables
./scope --target eac5 --no-dependency
```

### Different Processing Modes

```bash
# Full conversion to Verus code
./scope --target eac5 --mode reason

# Rule-based checking for analysis
./scope --target alp13 --mode rule

# Raw document parsing
./scope --target alp12 --mode raw
```

### PDF Processing Workflows

```bash
# Direct PDF processing
./scope --input-type pdf --target eac5

# PDF processing with rule-based analysis
./scope --input-type pdf --target alp14 --mode rule
```

## Supported Specifications

| Target | Specification version |
|---------------|-------------|
| eac5 | 1.0-eac5 |
| rel0 | 1.0-rel0 |
| alp11 | 1.1-alp11 |
| alp12 | 1.1-alp12 |
| alp13 | 1.1-alp13 |
| alp14 | 1.1-alp14 |

## Output Files

The scope generates different outputs based on the processing mode:

- **Reasoning Mode**: Generate Verus verification code
- **Rule-based checks Mode**: Analysis reports and validation results
- **Raw Mode**: Parsed specification data and dependencies

## Troubleshooting

### PDF Processing Issues

```bash
# Check if pdftotext is installed
pdftotext -v

# Install if missing
sudo apt-get install poppler-utils

# Verify PDF file exists
ls -la DEN0137_1.0-eac5_rmm-arch_external.pdf
```

### Common Errors

1. **"PDF file does not exist"**: Ensure the PDF file is present
2. **"pdftotext is not available"**: Install poppler-utils
3. **"Target version not supported"**: Use a supported specification

## Architecture

The scope consists of several key components:

1. **Document Preprocessor**: Cleans and normalizes specification text
2. **Type Parser**: Extracts enums, structs, and type definitions
3. **Interface Parser**: Processes command interfaces and conditions
4. **Code Generator**: Converts specifications to Verus code

## License

Apache-2.0 license 

## Support

For issues and questions:
- Check the troubleshooting section
- Review the [USAGE.md](USAGE.md) for detailed examples
- Upload issues in Issues page
