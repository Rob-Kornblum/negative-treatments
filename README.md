# negative-treatments

## Overview

This project extracts negative treatments from court opinions using OpenAI's language models. These are cases that are (overruled - wholly or partially, criticized, questioned, or limited). It includes prompt engineering, unit tests, and package management.

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/rob-kornblum/negative-treatments.git
cd negative-treatments
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get an OpenAI API Key

- Sign up or log in at [OpenAI](https://platform.openai.com/).
- Go to your [API keys page](https://platform.openai.com/api-keys) and create a new secret key.

### 5. Set Up Your `.env` File

Create a file named `.env` in the project root with the following content:

```
OPENAI_API_KEY=sk-...
```

Replace `sk-...` with your actual OpenAI API key.

---

## Running Unit Tests

To run all unit tests and verify your environment, run this command from the project root directory:

```bash
pytest
```

---

## Using the Extraction Function in Python

You can test the extraction function interactively in a Python shell:

```python
from extract import extract_negative_treatments

# Replace 'YOUR_CASE_ID' with a valid case ID for your data source
treatment = extract_negative_treatments(id='YOUR_CASE_ID')
print(treatment)
```

- The function will return a list of dictionaries, each with the keys: `treated_case`, `treatment`, `treatment_text`, and `explanation`.

---

## Running the FastAPI Server

If you want to run the API server:

```bash
uvicorn main:app --reload
```

---

## Prompt Engineering

### Prompting Approaches Attempted

**v1:**  
The initial prompt just asked for negative treatments and provided a single example. This led to over-inclusion of cases in some instances because the model often returned any cited case, even if it was just mentioned or used as background, since there were no explicit instructions or negative examples.

**v2:**  
To address over-inclusion, v2 introduced explicit limitations and examples, especially distinguishing between actual negative treatment and mere requests by parties (e.g., “The State requests that we overrule…”). However, the model still sometimes included cases that were not truly negatively treated, like when the court cited a case to support its reasoning.

**v3:**  
v3 added the limitation that cases cited only as support for the court’s reasoning (not actually criticized or overruled) should not be included. It provided both positive and negative examples for this scenario, such as Hack v. Hack being cited as support. While this reduced false positives, the model still sometimes misclassified partial overrulings as full overrulings and included cases mentioned but not regatively treated.

**v4:**  
v4 introduced more step-by-step instructions, instructing the model to err on the side of exclusion, and detailed JSON examples. It also clarified how to handle partial negative treatments (e.g., “Partially Overruled” for cases overruled only to the extent inconsistent with the current holding). While this version successfully handled partially overruled cases, it was still including negative treatments from concurrences, dissents, or footnotes.

**v5:**  
v5 added the explicit instruction: **ignore negative treatments that appear only in concurrences, dissents, or footnotes—extract only from the main majority opinion**. This was necessary because the model previously included negative treatments from these sections, which are not authoritative for the main holding.

---

## Package Management

All dependencies are listed in `requirements.txt`.  
If you prefer [Poetry](https://python-poetry.org/), you can convert the requirements file using Poetry’s import command.

---

## Troubleshooting

- Make sure your `.env` file is present and contains a valid OpenAI API key.
- Activate your virtual environment before running any commands.