import pytest
from unittest.mock import patch, MagicMock
from extract import fetch_case_html, extract_opinion_text, load_prompt, extract_negative_treatments

def test_fetch_case_html_success(monkeypatch):
  class MockResponse:
    def __init__(self, text):
      self.text = text
    def raise_for_status(self):
      pass
  def mock_get(url, headers):
    return MockResponse("<html>case content</html>")
  monkeypatch.setattr("requests.get", mock_get)
  html = fetch_case_html("12345")
  assert "<html>case content</html>" in html

def test_extract_opinion_text_with_opinion():
  html = '''
  <div id="gs_opinion">
    <p>This is the opinion.</p>
    <p>Save trees - read court opinions online on Google Scholar.</p>
    <p>Another paragraph.</p>
  </div>
  '''
  result = extract_opinion_text(html)
  assert "This is the opinion." in result
  assert "Save trees" not in result
  assert "Another paragraph." in result

def test_extract_opinion_text_without_opinion():
  html = "<html><body>No opinion here</body></html>"
  result = extract_opinion_text(html)
  assert result == ""

def test_load_prompt(tmp_path):
  prompt_file = tmp_path / "prompt.txt"
  prompt_file.write_text("Opinion: {{ opinion_text }}")
  result = load_prompt("Test opinion", str(prompt_file))
  assert "Test opinion" in result

@patch("extract.fetch_case_html")
@patch("extract.extract_opinion_text")
@patch("extract.load_prompt")
@patch("extract.OpenAI")
@patch("extract.load_dotenv")
def test_extract_negative_treatments_success(mock_dotenv, mock_openai, mock_load_prompt, mock_extract_opinion, mock_fetch_html, monkeypatch):
  mock_fetch_html.return_value = "<html>mock</html>"
  mock_extract_opinion.return_value = "mock opinion"
  mock_load_prompt.return_value = "mock prompt"
  mock_client = MagicMock()
  mock_response = MagicMock()
  mock_choice = MagicMock()
  mock_choice.message.content = '[{"treated_case":"Case A","treatment":"overruled","treatment_text":"text","explanation":"explanation"}]'
  mock_response.choices = [mock_choice]
  mock_client.chat.completions.create.return_value = mock_response
  mock_openai.return_value = mock_client
  monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
  result = extract_negative_treatments("12345")
  assert isinstance(result, list)
  assert result[0]["treated_case"] == "Case A"
  assert "treatment" in result[0]
  assert "treatment_text" in result[0]
  assert "explanation" in result[0]

@patch("extract.fetch_case_html")
@patch("extract.extract_opinion_text")
@patch("extract.load_prompt")
@patch("extract.OpenAI")
@patch("extract.load_dotenv")
def test_extract_negative_treatments_no_json(mock_dotenv, mock_openai, mock_load_prompt, mock_extract_opinion, mock_fetch_html, monkeypatch):
  mock_fetch_html.return_value = "<html>mock</html>"
  mock_extract_opinion.return_value = "mock opinion"
  mock_load_prompt.return_value = "mock prompt"
  mock_client = MagicMock()
  mock_response = MagicMock()
  mock_choice = MagicMock()
  mock_choice.message.content = 'No JSON here'
  mock_response.choices = [mock_choice]
  mock_client.chat.completions.create.return_value = mock_response
  mock_openai.return_value = mock_client
  monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
  result = extract_negative_treatments("12345")
  assert result == []

def test_extract_negative_treatments_api_key_none(monkeypatch):
  monkeypatch.setattr("os.getenv", lambda key, default=None: None if key == "OPENAI_API_KEY" else default)
  with pytest.raises(ValueError):
    extract_negative_treatments("12345")

def test_extract_negative_treatments_api_key_blank(monkeypatch):
  monkeypatch.setenv("OPENAI_API_KEY", "")
  with pytest.raises(ValueError):
    extract_negative_treatments("12345")