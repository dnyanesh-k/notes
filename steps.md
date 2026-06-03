Here's a narration script you can follow while screen recording:

---

**[Scene 1 — Show the repo / file structure]**

> "I built a Python CLI alarm clock — no dependencies, stdlib only. Before writing any code I defined the problem: what does an alarm clock actually need as a CLI tool? Set, list, cancel, and a daemon that fires alarms. I cut everything else."

---

**[Scene 2 — Show README engineering decisions table]**

> "I made explicit decisions upfront — JSON for persistence so it survives restarts, argparse over click so there's nothing to install, powershell beep on WSL because terminal bell gets throttled. These are documented in the README, not just in my head."

---

**[Scene 3 — Show git log]**

```bash
git log --oneline
```

> "Each commit is one feature. You can read the history like a story — scaffold, persistence, CLI, notifier, runner, edge cases. No fat commits, no 'fix stuff' messages."

---

**[Scene 4 — Live demo]**

```bash
python3 alarm_clock.py set 00:42 "Demo alarm"
python3 alarm_clock.py list
python3 alarm_clock.py start
```

> "Set an alarm, list it, start the daemon. When it fires you get a bold red alert and 4 beeps. Press s to snooze, d to dismiss."

*(wait for alarm to fire, show the prompt, press d)*

---

**[Scene 5 — Show the log file]**

```bash
cat ~/alarm_clock/alarm_clock.log
```

> "Every event is logged — set, fired, cancelled, snoozed. If the alarm fires while you're away you have proof it ran."

---

**[Scene 6 — Close]**

> "The goal wasn't to build the most features. It was to make the right decisions, test incrementally, and leave a clean codebase someone else can read and extend."

---

**Tips for recording:**
- Use [OBS](https://obsproject.com) or just Windows Game Bar (`Win + G`) to record
- Keep terminal font large — 16pt minimum
- Record in one take, mistakes are fine — shows real process