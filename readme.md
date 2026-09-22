# ResearchNet

Live networking graph for in-person events: React + Neo4j Aura + [react-force-graph](https://github.com/vasturiano/react-force-graph).

Created from the DemoNet template, with its own Aura instance and GitHub Pages site.

Live site: [https://awuchen.github.io/ResearchNet](https://awuchen.github.io/ResearchNet)

## What is included

- NFC / URL card tap: first tap of your own card registers the phone (`Yes, this is me`)
- Later taps of someone else's card create a `CONNECTED_TO` relationship
- Force-directed graph, node profiles (name, role/company, LinkedIn, email)
- Timeline view and natural-language search

## Neo4j

Connection defaults are in `react-graph-viz/src/neo4jConfig.js` (Aura **398ffc2d**, instance name **ResearchNet**). Override with `REACT_APP_NEO4J_URI`, `REACT_APP_NEO4J_USERNAME`, `REACT_APP_NEO4J_PASSWORD`, `REACT_APP_NEO4J_DATABASE` in `react-graph-viz/.env` before `npm run build` / deploy.

**Authentication failure:** reset the Aura password, paste it into `neo4jConfig.js` (and Cred), then rebuild.

Aura Free pauses after ~72 hours with no queries. Keep-alive is two layers:

1. The live app pings every 30 minutes while a tab is open (`react-graph-viz/src/neo4jKeepAlive.js`).
2. GitHub Actions on `main` pings every 6 hours (`.github/workflows/neo4j-keepalive.yml`) and weekly-commits `.github/neo4j-keepalive.stamp` so GitHub does not disable the cron after 60 days of inactivity.

Set repo secrets `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`, then `gh workflow enable "Neo4j Keep-Alive"` and run it once.

The main app lives in `react-graph-viz/`. Use `npm install` and `npm start` there for local development.
