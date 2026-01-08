## LLM Agent Baseline

### Prerequisites

**1. Install dependencies**
```bash
sudo apt install python3-pypdf
sudo apt install python3-networkx
sudo apt install python3-openai
```

**2. Prepare the RMM specification**
```bash
// rename the target PDF into cca.pdf 
cp DEN0137_1.0-rel0_rmm-arch_external.pdf ./llm_baseline/cca.pdf
```

### About the tool

This is the baseline used to evaluate the LLM model's ability to find inconsistency errors in specs. The LLM agent contains two steps:

1. Cut the document into components to fit for the LLM's context window
2. Automatically build connection as dependencies among components as context
3. Run each component and its relevant dependencies as input to the models


Please add your api key to the file to run the program, the `***.gh` is the dependency graph extracted by the agent and `***.kvs` is the python pickle object of the mapping. 

For a new document, we need user's help on preparing input of the document's table contents start page number and end page number.
With the ranges of table of contents, the agent autotmatically parse the document into individual sections with dependencies, and feed the target section with its context to LLM.

Run the command:

        python3 main.py cca.pdf 8 15


The sample output is in [llm_output.txt](./llm_output.txt)
