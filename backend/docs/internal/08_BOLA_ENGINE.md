# BOLA engine

For path templates containing an identifier, the MVP substitutes the safe fixture identifier `1`, obtains tokens for both supplied identities, and compares both responses. A confirmed finding requires both identities to receive HTTP 200 and equivalent JSON resource content; status 200 alone is not sufficient. Evidence records statuses and a boolean resource match, never tokens.
