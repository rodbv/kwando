# How These Forecasts Work

## What is Monte Carlo Simulation?
Monte Carlo simulation is a mathematical technique that helps us make predictions in uncertain environments. In software delivery, we use it to forecast delivery dates or team capacity by:
1. Looking at our historical completion data (how long items actually took)
2. Running thousands of "simulations" using random samples from this history
3. Analyzing the results to provide confidence levels

## What Data Are We Using?
- We analyze your team's actual weekly throughput (how many items were completed per week)
- You can provide data in two ways:
  - **CSV file**: Each row represents one week of historical throughput data
  - **Direct text input**: Enter comma-separated values (e.g., `2,3,5,2,4,6`) directly in the dashboard
- We use this real data rather than estimates because it includes all the natural variation in your delivery system
- Throughput captures your team's actual delivery capacity, accounting for all the factors that affect completion rates

## How to Read the Results
- The forecasts show different confidence levels (70% to 98%)
- An "80% confidence" means that, based on your historical performance, you have an 80% chance of hitting that target
- Higher confidence levels (90%, 95%) give you more certainty but predict longer durations
- Lower confidence levels (70%, 80%) are more aggressive but carry more risk

## Key Concepts
1. **Using History vs Estimates**: Rather than relying on up-front estimates, we use your actual delivery history. This captures your team's real-world performance including all the normal delays and uncertainties.

2. **Probabilistic vs Deterministic**: Instead of a single date, we provide a range of possibilities with confidence levels. This better reflects the inherent uncertainty in knowledge work.

3. **System Thinking**: The throughput values reflect your entire delivery system - not just coding time but also reviews, testing, deployments, and any delays. This gives you a more realistic picture of your team's actual delivery capacity.

## When to Use Each Simulation
- **"When will it be done?"** - Use when you have a specific number of work items and need to forecast completion dates
- **"How many items?"** - Use when you have a time period and need to forecast how many items you can complete

## Making Better Decisions
- Use higher confidence levels (90%+) for important commitments or dependencies
- Use lower confidence levels (70-80%) for internal planning or less critical items
- Look for ways to increase your throughput to improve all forecasts
- Remember: the goal is to make informed decisions, not to get exact predictions

## Learn More

**Books by Daniel Vacanti:**
- [Actionable Agile Metrics for Predictability](https://actionableagile.com/books/aamfp) - The definitive guide to flow metrics and analytics
- [When Will It Be Done?](https://leanpub.com/whenwillitbedone) - Lean-Agile Forecasting to Answer Your Customers' Most Important Question
- [Actionable Agile Metrics Volume II](https://actionableagile.com/books/aamfp-vol2) - Advanced Topics in Predictability

**Additional Resources:**
- [ProKanban.org](https://prokanban.org/) - Community for learning about Kanban and flow metrics
- [Why Monte Carlo Simulation?](https://www.youtube.com/watch?v=j1FTNVRkJYg) - Video explanation by Daniel Vacanti

*Based on concepts from ActionableAgile™ and "Actionable Agile Metrics for Predictability" by Daniel Vacanti.*
