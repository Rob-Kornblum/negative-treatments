# negative-treatments

## Overview

This project extracts negative treatments from court opinions on google scholar using OpenAI's gpt-4o-mini language model. These are cases that are overruled - wholly or partially, criticized, questioned, or limited.

The `gpt-4o-mini` model was chosen for its balance of accuracy, speed, and cost-effectiveness. Here, we need it for targeted, reliable outputs with the same instructions across a range of input opinion text rather than general-purpose chat.

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

```txt
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

```bash
python
from extract import extract_negative_treatments

# Replace 'CASE_ID' with a valid case ID from the google scholar database (e.g., https://scholar.google.com/scholar_case?case=<CASE_ID>)
treatments = extract_negative_treatments(id='CASE_ID')
print(treatments)
```

- The function will return a list of dictionaries, each with the keys: `treated_case`, `treatment`, `treatment_text`, and `explanation`.

```bash
[{'treated_case': 'Plaintiff v. Defendant, Del.Supr., 123 A.2d 456 (1999)', 'treatment': 'Overruled', 'treatment_text': 'We hereby overrule Plaintiff.', 'explanation': 'The opinion explicitly overrules Plaintiff.'}]
```

- If no negative treatments are found, the function will return an empty list:

```bash
[]
```

---

## Running the FastAPI Server

If you want to run the API server:

```bash
uvicorn main:app --reload
```

Navigate to http://localhost:8000/docs in your browser to use the FastAPI UI

Click on `Get Negative Treatments` (the `/negative-treatments` endpoint) and click `Try it out`.

Replace the word `string` with a valid case ID from the google scholar database.

Example:

```json
{
  "case_id": "123456789"
}
```

Click `Execute` to send the request

Example output:

```json
{
  "negative_treatments": [
    {
      "treated_case": "Plaintiff v. Defendant, Del.Supr., 123 A.2d 456 (1999)",
      "treatment": "Overruled",
      "treatment_text": "We hereby overrule Plaintiff.",
      "explanation": "The opinion explicitly overrules Plaintiff."
    }
  ]
}
```

---

## Prompting Approaches Attempted

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

---

## Troubleshooting

- Make sure your `.env` file is present and contains a valid OpenAI API key.
- Activate your virtual environment before running any commands.
- Ensure your case_ids are wrapped in quotation marks (either `"` or `'` if running `extract_negative_treatments` via the python console or `"` if using the FastAPI UI).