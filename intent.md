# Hello World Agent

Simple Hello World conversational agent for testing and demonstration purposes.

## Business challenge

Build a minimal AI agent that greets users, responds to basic messages, and demonstrates a simple conversational flow — intended for testing agent scaffolding and as a reference implementation.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Agent responds to greeting | — | 100% correct greeting response | Day 1 | Conversational AI testing | agent-derived |
| Basic message handling works end-to-end | — | Agent deployed and reachable | Day 1 | Agent scaffolding validation | agent-derived |

## Key Milestones

1. **Agent scaffold ready** — project structure bootstrapped with all required files
2. **Greeting flow works** — agent correctly greets the user on first interaction
3. **Basic conversation loop** — agent handles follow-up messages and responds meaningfully
4. **Tests passing** — prebuilt and custom tests confirm correct behaviour
5. **Agent deployed** — agent is live and reachable via A2A endpoint

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash for High Volume Subscription and Usage Business (software provider)

### Process Hierarchy

```
Lead to Cash for High Volume Subscription and Usage Business
└── Opportunity to Quote (software provider)
    └── Sell products and services (software provider)
        └── Demonstrate software
        └── Manage software product trials
```

### Summary

A Hello World test agent maps loosely to software demonstration activities; in practice it is a standalone custom development with no direct RBA coverage.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|---------------------|------|---------------------|
| Conversational greeting and response | None relevant | — | — | — | — | Yes | Custom Python agent required |
| Simple message handling | None relevant | — | — | — | — | Yes | Custom logic in agent.py |

### Key findings

- No standard SAP product covers a Hello World test agent — fully custom implementation.
- A pro-code Python agent (A2A protocol) is the correct and simplest approach.
- No MCP tool integrations required; agent uses only its built-in LLM reasoning.
- Implementation is intentionally minimal: greet, respond, repeat.
- All complexity is in scaffolding correctness, not business logic.

## Recommendations

### Hello World Python Agent

#### Executive Summary

Minimal Python A2A agent for greeting and basic conversation.

#### Recommended Solution

A pro-code Python agent built on the SAP Joule Studio A2A runtime. The agent has a simple system prompt instructing it to greet the user and respond helpfully to any message. No MCP servers or external tool calls are wired in. This serves as a clean reference implementation and test baseline.

#### Recommended solution category

AI Agent

#### Intent fit
95%
