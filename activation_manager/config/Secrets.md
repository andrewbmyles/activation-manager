# Secrets Configuration

API keys should be stored in environment variables, not in code.

## Environment Variables

Set these in your `.env` file:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit API keys to version control!