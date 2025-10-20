
inspiration: 
"""
Most engineers treat AI context windows like infinite RAM.

Your agent fails not because the model is bad, but because you're flooding 200K tokens with noise and wondering why it hallucinates.

After building agentic systems for production teams, I've learned: 𝗔 𝗳𝗼𝗰𝘂𝘀𝗲𝗱 𝗮𝗴𝗲𝗻𝘁 𝗶𝘀 𝗮 𝗽𝗲𝗿𝗳𝗼𝗿𝗺𝗮𝗻𝘁 𝗮𝗴𝗲𝗻𝘁.

Context engineering isn't about cramming more information in. It's about systematic management of what goes in and what stays out.

𝗧𝗵𝗲 𝗥𝗲𝗱𝘂𝗰𝗲 𝗦𝘁𝗿𝗮𝘁𝗲𝗴𝘆: 𝗦𝘁𝗼𝗽 𝗪𝗮𝘀𝘁𝗶𝗻𝗴 𝗧𝗼𝗸𝗲𝗻𝘀

𝗧𝗵𝗲 𝗠𝗖𝗣 𝗦𝗲𝗿𝘃𝗲𝗿 𝗧𝗿𝗮𝗽:
Most teams load every MCP server by default. I've seen 24,000+ tokens (12% of context) wasted on tools the agent never uses.

𝗧𝗵𝗲 𝗙𝗶𝘅:
• Delete your default MCP.json file
• Load MCP servers explicitly per task
• Measure token cost before adding anything permanent

This one change saves 20,000+ tokens instantly.

𝗧𝗵𝗲 𝗖𝗟𝗔𝗨𝗗𝗘.𝗺𝗱 𝗣𝗿𝗼𝗯𝗹𝗲𝗺:
Teams build massive memory files that grow forever. 23,000 tokens of "always loaded" context that's 70% irrelevant to the current task.

𝗧𝗵𝗲 𝗦𝗼𝗹𝘂𝘁𝗶𝗼𝗻:
• Shrink CLAUDE.md to absolute universal essentials only
• Build `/prime` commands for different task types
• Load context dynamically based on what you're actually doing

𝗘𝘅𝗮𝗺𝗽𝗹𝗲:
```
/prime-bug → Bug investigation context
/prime-feature → Feature development context
/prime-refactor → Refactoring-specific context
```

Dynamic context beats static memory every time.

𝗧𝗵𝗲 𝗠𝗲𝗻𝘁𝗮𝗹 𝗠𝗼𝗱𝗲𝗹 𝗦𝗵𝗶𝗳𝘁

Stop thinking: "How do I get more context in?"
Start thinking: "How do I keep irrelevant context out?"

𝗪𝗵𝗮𝘁 𝗦𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝘀 𝗪𝗶𝗻𝗻𝗲𝗿𝘀 𝗳𝗿𝗼𝗺 𝗟𝗼𝘀𝗲𝗿𝘀:
✓ Winners: Measure token usage per agent operation
✗ Losers: "Just throw everything in the context"

✓ Winners: Design context architecture before writing prompts
✗ Losers: Keep adding to claude.md when agents fail

Your agent's intelligence ceiling is your context management ceiling.

---

What's the biggest waste of tokens in your AI setup right now?

hashtag#ContextEngineering hashtag#AgenticEngineering hashtag#AIAgents hashtag#DeveloperProductivity hashtag#SoftwareArchitecture

[Human Generated, Human Approved]
"""

1) I want you to build me a linkedin post from the perspective of a side project/learning i'm doing. I like the perspective of: https://www.linkedin.com/in/hoenig-clemens-09456b98 and how he talks about his side projects. 

3) Also, see how i can make the mcp server better using this inspriation and this context engineering guide: https://github.com/coleam00/context-engineering-intro to deliver a version 2 project plan.