# Student 3 AI integration

Student 3 receives the validated `ScanResult` JSON. The scanner establishes deterministic technical evidence; the AI layer converts it into explanations, remediation guidance, implementation options, and validation tests. Consume `findings`, `evidence`, `pocs`, `score`, `target`, `summary`, and `statistics`. Do not send the original credential request or raw Authorization headers to the AI layer. Do not present generated code as a deployable patch without source-code context and developer review.
