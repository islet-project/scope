# CCA Specification Converter - Usage Guide

This guide provides detailed usage instructions for the CCA Specification Converter, including command line options, processing modes, and examples.

## Table of Contents

1. [Command Line Interface](#command-line-interface)
2. [Processing Modes](#processing-modes)
3. [Input Types](#input-types)
4. [Examples](#examples)

## Command Line Interface

### Quick Commands to Follow

#### Formal Reasoning

This reproduces section 7.1.
```bash
(generate a model)
./scope --target {eac5, rel0} --input-type pdf --mode reason > {eac5, rel0}.rs

(apply a patch to avoid type errors)
patch -p0 < ./patch/{eac5, rel0}.patch
cp {eac5, rel0}.rs ~/

(install verus)
cd ~
git clone https://github.com/verus-lang/verus.git
cd verus
git reset --hard bec74a67d9281a4f51a7e1855760c5d16d8f63ff
cd ./source
./tools/get-z3.sh (on Unix/macOs) 
source ../tools/activate
vargo build --release

(verify)
./target-verus/release/verus ~/{eac5, rel0}.rs
```

#### Rule-based Checks

This reproduces section 7.1.
```bash
(perform heuristic checks)
./scope --target {eac5, rel0} --input-type pdf --mode rule > {eac5, rel0}_rule.txt

(apply a patch for pre-determined labelling)
patch -p0 < ./patch/{eac5, rel0}_rule.patch

(see the result)
cat {eac5, rel0}_rule.txt
```

#### Measure Covered Rates

This reproduces section 7.2.2 and 7.3.
```bash
./scope --target {eac5, rel0, alp11, alp12} --input-type pdf --mode reason --is-coverage --no-dependency > {eac5, rel0, alp11, alp12}_coverage.rs

(apply a patch for pre-determined labelling)
patch -p0 < ./patch/{eac5, rel0, alp11, alp12}_coverage.patch
cp {eac5, rel0, alp11, alp12}_coverage.rs ~/

(verify)
./target-verus/release/verus ~/{eac5, rel0, alp11, alp12}_coverage.rs

(see the result)
cat ~/{eac5, rel0, alp11, alp12}_coverage.rs
```

### Basic Syntax

```bash
./scope [--target TARGET] [--mode MODE] [--input-type TYPE]
```

### Options Reference

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--target` | eac5, rel0, alp11, alp12, alp13, alp14 | eac5 | Target specification to process |
| `--mode` | reason, rule, raw | reason | Processing mode |
| `--input-type` | txt, pdf | txt | Input file type |
| `--no-dependency` | flag | false | Skip dependency processing and output |

### Help System

```bash
# Display help message
./scope --help

# Show current version and settings
./scope --target eac5 --mode reason --input-type txt
```

## Processing Modes

### 1. Reasoning Mode (`--mode reason`)

**Purpose**: Full conversion from specification to Verus verification code

**Use Cases**:
- Formal verification of targeted properties
- Generating complete Verus specifications
- Academic research and proof development

**Output**: Complete Verus code with type definitions, function specifications, and proof obligations

**Example**:
```bash
./scope --target eac5 --mode reason --input-type txt
```

**Generated Output Structure**:
```verus
use vstd::prelude::*;

verus! {
    // Type definitions
    pub enum RmiStatusCode { ... }
    
    // Struct definitions  
    struct RmmRealmParams { ... }
    
    // Function specifications
    pub open spec fn rmi_version_spec(...) -> bool { ... }
    
    // Proof obligations
    pub proof fn rmi_version_rule(...) { ... }
}
```

### 2. Rule-based checks Mode (`--mode rule`)

**Purpose**: Analysis and validation without code generation

**Use Cases**:
- Finding dangling outputs and footprint issues
- Specification consistency checking

**Output**: Analysis reports highlighting potential issues

**Example**:
```bash
./scope --target alp14 --mode rule --input-type pdf
```

**Typical Output**:
```
--------------------------------------------
RMI_VDEV_CREATE command
dangling_output_1
dangling_output_2

--------------------------------------------
RMI_VDEV_DESTROY command
missing_footprint_item
```

### 3. Raw Mode (`--mode raw`)

**Purpose**: Document parsing without processing or conversion

**Use Cases**:
- Understanding specification structure
- Debugging parsing issues
- Extracting raw data for analysis

**Output**: Parsed specification data and dependencies

**Example**:
```bash
./scope --target rel0 --mode raw --input-type txt
```

## Input Types

### Text Input (`--input-type txt`)

**Description**: Process pre-converted text files

**Prerequisites**: Text file must exist (e.g., `eac5.txt`)

**Advantages**:
- Faster processing (no conversion step)
- Suitable for repeated processing
- Better for development and testing

**Example**:
```bash
./scope --target eac5 --input-type txt --mode reason
```

### PDF Input (`--input-type pdf`)

**Description**: Automatically convert PDF files to text

**Prerequisites**: 
- PDF file must exist (e.g., `DEN0137_1.0-eac5_rmm-arch_external.pdf`)
- `pdftotext` must be installed

**Advantages**:
- Direct processing of original specifications
- No manual conversion required
- Consistent conversion settings

**Setup**:
```bash
# Install PDF processing dependencies
sudo apt-get install poppler-utils

# Verify installation
pdftotext -v
```

**Example**:
```bash
./scope --target eac5 --input-type pdf --mode reason
```

## Examples

### Basic Workflows

#### 1. Quick Start with Defaults
```bash
# Uses EAC5 specification, text input, reasoning mode
./scope
```

#### 2. Process Different Specifications
```bash
# Process ALP14 specification
./scope --target alp14

# Process REL0 specification with PDF input
./scope --target rel0 --input-type pdf
```

#### 3. Different Analysis Modes
```bash
# Full conversion to Verus code
./scope --target eac5 --mode reason

# Rule-based checks
./scope --target alp14 --mode rule

# Raw parsing for debugging
./scope --target rel0 --mode raw
```

#### 4. Skip Dependency Processing
```bash
# Generate only RMM model without dependency analysis
./scope --target eac5 --no-dependency

# Print parsed raw data without dependency information
./scope --mode raw --no-dependency
```

### Advanced Usage

#### Dependency Processing Control

The `--no-dependency` flag provides control over dependency analysis:

**What it skips**:
- Dependency collection from Architecture section
- RIPAS/HIPAS state transition analysis
- Dependency proof function generation (in reasoning mode)
- Dependency table output (in raw mode)

**When to use it**:
- Focus on command specifications only (RMM model)
- When dependency analysis is not relevant

**Examples**:
```bash
# Print only command-related information
./scope --target alp14 --mode raw --no-dependency

# Generate Verus code without dependency proofs
./scope --target eac5 --mode reason --no-dependency
```
