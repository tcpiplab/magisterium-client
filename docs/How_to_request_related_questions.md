# Adding Request for Inclusion of Related Questions

Magisterium AI API can also return related questions in the response object via the related_questions field. This field is optional. In order to return related questions, you must set the return_related_questions parameter to true in your request.

```python
url = "https://www.magisterium.com/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "model": "magisterium-1",
    "messages": [
    {
        "role": "user",
        "content": "What is the Magisterium?",
    }
    ],
    "stream": False,
    "return_related_questions": True
}
```

Related questions will be included in the response object as an array of strings.

```json
{
  "object": "chat.completion",
  "related_questions": [
    "What is the Magisterium's teaching on faith and morals?",
    "What is the Magisterium's teaching on Scripture?",
    "What is the Magisterium's teaching on tradition?",
  ],
  // other fields ...
}
```
