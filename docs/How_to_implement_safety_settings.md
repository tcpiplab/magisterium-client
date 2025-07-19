# Safety Settings

Magisterium AI API offers user-customizable safety settings to moderate the incoming requests to the API. This moderation is currently limited to the input, not the output.

## Safety Settings Behavior

If one of the safety settings is triggered, the response will either:

- contain fallback response if response is set to true in the safety settings (defaults to true), or
- set finish_reason to content_filter and outputs a blank text.

## Example

Include `safety_settings` in your request:

```json
{
  "model": "magisterium-1",
  "messages": [
    // your messages here
  ],
  "safety_settings": {
    "CATEGORY_NON_CATHOLIC": {
      "threshold": "BLOCK_ALL",
      "response": true
    },
  },
  // other fields ...
}
```

## Categories and Thresholds

The following safety categories and thresholds are supported:

| Category              | Description                                                                 | Thresholds      | Default    |
|-----------------------|-----------------------------------------------------------------------------|-----------------|------------|
| CATEGORY_NON_CATHOLIC | Queries entirely unrelated to Catholicism, religion, faith and morals.      | BLOCK_ALL, OFF  | BLOCK_ALL  |

