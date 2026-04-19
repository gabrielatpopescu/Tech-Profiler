<script lang="ts">
  const sections = [
    {
      title: "The Goal",
      description: "Equipping the Sales Team with competitive market intelligence."
    },
    {
      title: "The Journey",
      description: "From Bash scripts to Python-powered headless browsers."
    },
    {
      title: "Debate Topics",
      description: "Addressing scaling, current limitations, and future discovery."
    },
    {
      title: "Results",
      description: "Extracting deep tech stacks from 200+ Shopify competitors."
    }
  ];

  const detectionMethods = [
    {
      title: "HTTP Headers & Meta Tags",
      description: "Fast, server-side technology signatures via X-Powered-By headers and custom meta tags.",
      example: "Detecting Cloudflare, HSTS policies, Nginx"
    },
    {
      title: "DOM & CSS Selectors",
      description: "Client-side framework indicators through unique DOM patterns, data attributes, and CSS rules.",
      example: "Shopify themes, WordPress plugins (Elementor), Vue/React roots"
    },
    {
      title: "JavaScript Runtime Variables",
      description: "Live JavaScript execution to detect global properties that static scrapers completely miss.",
      example: "window.Shopify, window.__NUXT__, framework globals"
    },
    {
      title: "DNS & SSL Context",
      description: "Capturing DNS records (TXT, NS, SOA) and SSL certificate issuers for infrastructure insights.",
      example: "Identifying mail providers, CDN networks, hosting platforms"
    }
  ];

  const thinkingProcess = [
    {
      phase: 1,
      title: "Bash Proof of Concept",
      description: "Started with a Bash script to quickly ping domains and inspect HTTP headers. It proved the concept but lacked the depth needed for modern, JS-heavy e-commerce sites."
    },
    {
      phase: 2,
      title: "The Golang & Docker Dilemma",
      description: "Considered Go and Docker for raw performance and parallelization. Decided against it for the MVP because it overcomplicated output file generation and reduced code flexibility for integration."
    },
    {
      phase: 3,
      title: "Switching to Python",
      description: "Pivoted to Python. It offers unparalleled simplicity, native Parquet handling via Pandas and Playwright integration for deep DOM/JS analysis, prioritizing quality over speed."
    },
    {
      phase: 4,
      title: "Handling the Memory",
      description: "Playwright is memory-intensive. I implemented ThreadPoolExecutor (6 workers) and a custom browser lifecycle manager that recycles instances after 25 tasks to prevent memory leaks."
    },
    {
      phase: 5,
      title: "Incremental Persistence",
      description: "Implemented auto-saving to output.json every 5 domains. This ensures the scraping process is resilient to crashes and allows resumable analysis."
    }
  ];

  const debateTopics = [
    {
      title: "1. Current Issues & Mitigation",
      content: "Main issue: Playwright headless browsers are heavy and significantly slow down execution compared to static scraping. Solution implemented: A browser connection pool that recycles after 25 tasks to manage RAM. Future fix: a hybrid approach, only route domains to Playwright if static scraping fails to find a JS framework signature.",
      tag: "Debate Topic"
    },
    {
      title: "2. Scaling to Millions (1-2 Months)",
      content: "A single Python script is not sufficient. I would transition to a distributed microservices architecture (Kubernetes) with RabbitMQ/Kafka. I would split the workload: a Golang-based ingestion layer would handle initial HTTP/HTML scraping and DNS lookups at scale. Only complex Single Page Applications (SPAs) would be offloaded to a dedicated cluster of Python/Playwright workers via RabbitMQ/Kafka queues.",
      tag: "Debate Topic"
    },
    {
      title: "3. Discovering New Technologies",
      content: "Static regex rules are inherently reactive. To discover new tech automatically, I'd implement an Unsupervised Machine Learning pipeline (Clustering) to group unknown, recurring JavaScript variables and DOM patterns across domains, flagging them for human review to create new signatures.",
      tag: "Debate Topic"
    }
  ];

  const results = [
    {
      metric: "Input Domains",
      value: "200",
      context: "From Parquet source file"
    },
    {
      metric: "Concurrency",
      value: "6 Threads",
      context: "Managed via ThreadPoolExecutor"
    },
    {
      metric: "Stealth Status",
      value: "Active",
      context: "playwright-stealth bypasses basic bots"
    }
  ];
</script>

<style>
  :root {
    --background: oklch(0.141 0.005 285.823);
    --foreground: oklch(0.985 0 0);
    --card: oklch(0.21 0.006 285.885);
    --primary: oklch(0.646 0.222 41.116);
    --muted: oklch(0.705 0.015 286.067);
  }

  :global(body) {
    background-color: var(--background);
    color: var(--foreground);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }

  .container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }

  .card {
    background: rgba(33, 6, 137, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.65rem;
    padding: 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .card:hover {
    background: rgba(33, 6, 137, 0.3);
    border-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }

  .section {
    padding: 5rem 0;
  }

  .heading {
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.2;
    letter-spacing: -0.02em;
    margin-bottom: 1rem;
  }

  .subheading {
    font-size: 2.25rem;
    font-weight: 700;
    margin-bottom: 3rem;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75;
  }

  .text-muted {
    color: rgba(255, 255, 255, 0.6);
  }

  .tag {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    background: rgba(255, 107, 53, 0.2);
    color: #ff6b35;
    margin-bottom: 1rem;
  }

  .phase-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    color: white;
    font-weight: bold;
    margin-right: 1rem;
    flex-shrink: 0;
  }

  .metric-box {
    text-align: center;
  }

  .metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }

  .timeline {
    position: relative;
    padding-left: 2rem;
  }

  .timeline::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, rgba(255, 107, 53, 0.5) 0%, rgba(255, 107, 53, 0.1) 100%);
  }

  .timeline-item {
    position: relative;
    margin-bottom: 2rem;
  }

  .timeline-item::before {
    content: '';
    position: absolute;
    left: -2.5rem;
    top: 0.5rem;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #ff6b35;
    border: 3px solid var(--background);
  }
</style>

<div class="min-h-screen" style="background-color: var(--background);">
  <nav class="sticky top-0 z-50 border-b" style="border-color: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); background: rgba(20, 6, 80, 0.5);">
    <div class="container py-4 flex justify-between items-center">

        <div class="w-10 h-10 rounded-lg" style="background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); display: flex; align-items: center; justify-content: center; font-weight: bold;">
            <span class="text-2xl font-bold" style="color: oklch(0.141 0.005 285.823);">Presentation - Popescu Gabriela-Teodora</span>
        </div>
        <h1 class="text-2xl font-bold" style="background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
          TechProfiler
        </h1>

      <div class="flex gap-8">
        <a href="https://github.com/gabrielatpopescu" target="_blank" class="text-sm font-semibold" style="color: #ff6b35;">View Code</a>
      </div>
    </div>
  </nav>

  <section class="section container">
    <div class="text-center mb-20">
      <h1 class="heading" style="color: var(--foreground);">
        Technology Profiler & <span class="subheading" style="display: inline;">Market Intelligence</span>
      </h1>
      <p class="text-lg text-muted max-w-2xl mx-auto mt-4">
        A scalable solution designed to identify the technology stack of online stores.
      </p>
    </div>
  </section>

  <section class="section container">
    <h2 class="subheading">The Development Journey</h2>
    <div class="timeline">
      {#each thinkingProcess as step (step.phase)}
        <div class="timeline-item card">
          <div class="flex items-start gap-4">
            <div class="phase-number">{step.phase}</div>
            <div>
              <h4 class="text-lg font-bold mb-2" style="color: var(--foreground);">{step.title}</h4>
              <p class="text-muted leading-relaxed">{step.description}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </section>

  <section class="section container">
    <h2 class="subheading">Multi-Layer Detection Vectors</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      {#each detectionMethods as method (method.title)}
        <div class="card">
          <h3 class="text-lg font-bold mb-2" style="color: var(--foreground);">{method.title}</h3>
          <p class="text-sm text-muted mb-3">{method.description}</p>
          <p class="text-xs text-muted italic">Example: {method.example}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="section container">
    <h2 class="subheading">Addressing the Debate Topics</h2>
    <div class="space-y-4">
      {#each debateTopics as topic (topic.title)}
        <div class="card border-l-4" style="border-left-color: #ff6b35;">
          <div class="flex items-start gap-3 mb-3">
            <span class="tag">{topic.tag}</span>
          </div>
          <h3 class="text-xl font-bold mb-3" style="color: var(--foreground);">{topic.title}</h3>
          <p class="text-muted leading-relaxed">{topic.content}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="section container">
    <h2 class="subheading">Execution Metrics</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each results as item (item.metric)}
        <div class="card">
          <div class="metric-box">
            <div class="metric-value">{item.value}</div>
            <h3 class="font-bold text-sm mb-2" style="color: var(--foreground);">{item.metric}</h3>
            <p class="text-xs text-muted">{item.context}</p>
          </div>
        </div>
      {/each}
    </div>
  </section>

  <section class="section container">
    <h2 class="subheading">The Final Tech Stack</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card">
        <h3 class="text-lg font-bold mb-3" style="color: #ff6b35;">Backend (Scraping Engine)</h3>
        <ul class="text-muted text-sm space-y-2">
          <li><strong>Python 3.14</strong> - Chosen for ecosystem integration and Pandas data handling</li>
          <li><strong>Playwright + Stealth</strong> - JavaScript execution bypassing basic anti-bot systems</li>
          <li><strong>ThreadPoolExecutor</strong> - Parallel processing for optimized throughput</li>
          <li><strong>DNS Resolver</strong> - Deep infrastructure profiling</li>
        </ul>
      </div>

      <div class="card">
        <h3 class="text-lg font-bold mb-3" style="color: #ff6b35;">Frontend (Presentation)</h3>
        <ul class="text-muted text-sm space-y-2">
          <li><strong>Svelte</strong> - Lightweight, reactive UI to cleanly present results</li>
          <li><strong>Tailwind CSS</strong> - Custom, maintainable design system</li>
          <li><strong>TypeScript</strong> - Type-safe components</li>
          <li><strong>JSON Data Loading</strong> - Reading directly from the Python output</li>
        </ul>
      </div>
    </div>
  </section>

  <footer class="border-t" style="border-color: rgba(255, 255, 255, 0.1); margin-top: 5rem;">
    <div class="container py-8 text-center text-sm text-muted">
      <p>Website Technologies Scraper (SW Engineer Intern Application)</p>
    </div>
  </footer>
</div>