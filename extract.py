import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
from jinja2 import Template

def fetch_case_html(case_id: str) -> str:
    url = f"https://scholar.google.com/scholar_case?case={case_id}"
    # Mimic a browser user-agent to reduce the chance of being blocked by Google Scholar's anti-bot measures
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_opinion_text(html: str) -> str:
    """Extracts the main opinion text from the Google Scholar case HTML, omitting Google Scholar footer."""
    soup = BeautifulSoup(html, "html.parser")
    opinion_div = soup.find("div", id="gs_opinion")
    if not opinion_div:
        return ""
    # Filter out the Google Scholar footer line
    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in opinion_div.find_all("p")
        if "Save trees - read court opinions online on Google Scholar." not in p.get_text()
    ]
    return "\n\n".join(paragraphs)

def load_prompt(opinion_text: str, prompt_path: str = "prompts/negative_treatment_v1.txt") -> str:
    with open(prompt_path, "r") as f:
        template_str = f.read()
    template = Template(template_str)
    return template.render(opinion_text=opinion_text)

def extract_negative_treatments(case_id: str, client: OpenAI):
    html = fetch_case_html(case_id)
    opinion_text = extract_opinion_text(html)
    prompt = load_prompt(opinion_text)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.2,
    )
    content = response.choices[0].message.content.strip()
    try:
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1:
            json_str = content[start:end+1]
            return json.loads(json_str)
        else:
            return []
    except Exception as e:
        return []