# OpenAI Compatible API Migration Guide

This project has been migrated from Google Genai to support OpenAI compatible APIs. This allows you to use various LLM providers including OpenAI, Azure OpenAI, local models, and other compatible services.

## Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following configuration:

```bash
# OpenAI Compatible API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

### Supported Providers

#### OpenAI
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

#### Azure OpenAI
```bash
OPENAI_API_KEY=your-azure-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
OPENAI_MODEL=gpt-4o
```

#### Local Models (Ollama)
```bash
OPENAI_API_KEY=ollama  # Can be any string for local models
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1:8b
```

#### Other Compatible Services
- Anthropic Claude (via proxy)
- Groq
- Together AI
- Fireworks AI
- And many others

## Changes Made

1. **Dependencies**: Replaced `langchain-google-genai` and `google-genai` with `langchain-openai` and `openai`
2. **Configuration**: Updated `Configuration` class to support OpenAI API settings
3. **LLM Initialization**: All LLM instances now use `ChatOpenAI` instead of `ChatGoogleGenerativeAI`
4. **Web Search**: Simplified web research function (note: you may want to integrate with a proper search API like Tavily or SerpAPI)

## Installation

After updating the configuration, install the new dependencies:

```bash
cd backend
pip install -e .
```

Or if using uv:

```bash
cd backend
uv sync
```

## Notes

- The web search functionality has been simplified in this migration. For production use, consider integrating with a proper search API.
- All model configurations now support custom base URLs, making it easy to switch between different providers.
- The structured output functionality is preserved and works with OpenAI compatible APIs.