# Vibesort

AI-powered array sorting using GPT.

## Usage

Install the package:
```bash
pip install vibesort
```

Set your API key as an environment variable. ``OPENAI_API_KEY`` enables the
OpenAI backend while ``ARK_API_KEY`` enables DouBao (Ark).
```bash
export OPENAI_API_KEY=your_openai_key
# or
export ARK_API_KEY=your_ark_key
# optional: export ARK_MODEL=ep-xxxxxx
```

```python
from vibesort import vibesort

result = vibesort([5, 2, 8, 1, 9])
print(result)  # [1, 2, 5, 8, 9]
```

## Test

```bash
pytest tests/
```

## Dependencies

- openai
- volcengine-python-sdk[ark]
- pydantic
- typing-extensions

⚠️ Requires an OpenAI or DouBao API key. Experimental project - not for production use.
