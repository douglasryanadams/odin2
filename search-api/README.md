This is an HTTP interface for retrieving data from search interfaces online.

# Workflow

1. Accepts request over HTTP
2. Documents request in shared Key/Value store
3. Dispatches processing to separate event loop
4. Responds to HTTP request with redirect URL for status checks
5. Event loop retrieves data from designated source
6. Event loop writes results to shared Key/Value store
7. Once event loop completes, it marks the request as "complete" in Key/Value store
8. Client eventually retrieves results and clears record
9. HTTP server in front of these caches results

# Brave API