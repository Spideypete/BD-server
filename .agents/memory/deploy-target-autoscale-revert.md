---
name: Discord bot deployment target reverting to autoscale
description: Always-on processes (Discord bots, RCON bots, websocket servers) must be deployed as "vm", not "autoscale" — and the target can end up as autoscale even after being explicitly set to vm.
---

Observed a case where a Discord bot deployment was correctly configured via `deployConfig({ deploymentTarget: "vm", ... })` and published successfully, but a later `getDeploymentInfo()` check showed `deploymentType: "autoscale"`. The bot appeared to "go offline" repeatedly — this matches autoscale's idle-scale-down behavior, not a crash (no errors/tracebacks in logs).

**Why:** Autoscale deployments spin down when there's no inbound HTTP traffic and spin back up on the next request. A Discord bot has no inbound HTTP traffic driving it (it holds a persistent gateway websocket), so autoscale will repeatedly kill and restart it, which looks like "the bot keeps going offline" to the user even though nothing is actually broken in the code.

**How to apply:** When a user reports a persistent/background process (bot, worker, long-lived socket server) "going offline" or "restarting" in production, don't just check application-level logs for crashes — call `getDeploymentInfo()` and verify `deploymentType === "vm"` first. If it shows `autoscale` despite prior vm configuration, re-run `deployConfig({ deploymentTarget: "vm", ... })` and have the user republish.
