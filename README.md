# Technology Profiler

This project uses the Warpalizer dataset and some additional data to profile technologies on websites.

## Run

To run

```
uv run main.py
```

Increase the number of workers for a faster result (default is 6) (higher -> faster but more resources used)

Increase the timeout for a slower but more accurate result (default is 30 seconds) (higher -> slower but more accurate)

Note: The script saves incrementally. If interrupted, it will resume where it left off.

## Analyze Output

To see the statistics (after running main)

```
uv run analyze_output.py
```

# Debate Topics

1. **Main issues** 
    - Playwright headless browsers are heavy and significantly slow down execution compared to static scraping.
    - Solution implemented: A browser connection pool that recycles after 25 tasks to manage RAM.
    - Future fix: a hybrid approach, only route domains to Playwright if static scraping fails to find a JS framework signature.

2. **Scaling to Millions (1-2 Months)**
    - A single Python script is not sufficient. I would transition to a distributed microservices architecture (Kubernetes) with RabbitMQ/Kafka.
    - I would split the workload: a Golang-based ingestion layer would handle initial HTTP/HTML scraping and DNS lookups at scale. Only complex Single Page Applications (SPAs) would be offloaded to a dedicated cluster of Python/Playwright workers via RabbitMQ/Kafka queues.

3. **New Technologies in the future**
    - I would implement an unsupervised machine learning pipeline focused on anomaly detection and clustering. As the tool crawls the web, it would collect recurring but unrecognized JavaScript global variables, unique file paths, and DOM patterns. When the system detects a cluster of identical unknown signatures appearing across thousands of different stores, it would automatically flag it as a potential new technology