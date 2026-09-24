# Rate limiting

The observation pass is bounded by the selected mode: easy 3 requests/1 worker, moderate 8/3, brutal 16/6. Results count 2xx, 4xx, 429, 5xx, and timeout outcomes. It stops on request errors or HTTP 5xx responses and marks the safety result aborted when degradation is observed. This is safe observation, not a stress or denial-of-service tool.
