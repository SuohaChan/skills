---
name: power-on-computer
description: Use when the user explicitly asks to remotely power on, start, or turn on their computer through the configured Bemfa MQTT-connected ESP8266 servo.
---

# Power On Computer

Send one authorized power-on command through Bemfa to the ESP8266 servo attached to the computer's power button.

## Local configuration

The real Bemfa UID belongs in the local `config.json`, which is intentionally ignored by Git. Start from `config.example.json` and fill in the local UID. The script also accepts a custom configuration path through `-ConfigPath` or the `BEMFA_CONFIG` environment variable.

Never commit or report the real UID. The example file contains placeholders only.

## Invocation contract

- Run only when the user explicitly requests that the computer be powered on now.
- If the request is ambiguous, ask before sending because pressing an already-running computer's power button may shut it down.
- Execute `scripts/power_on.ps1` exactly once.
- Do not retry a timeout or failed request automatically; a retry could press the physical button twice.
- Report the script result. API acceptance confirms command delivery to Bemfa, not that the computer actually booted.

## Command

From this skill directory, run:

```powershell
& '.\scripts\power_on.ps1'
```

For a non-default configuration path:

```powershell
& '.\scripts\power_on.ps1' -ConfigPath '.\config.json'
```

For non-mutating diagnostics, use `-DryRun`; it validates and displays the request contract without sending the command.

## Quick reference

| Setting | Fixed value |
|---|---|
| Bemfa topic | `computerPower` |
| Message type | `1` |
| Message | `on` |
| Automatic retries | None |

## Common mistakes

- A successful HTTP response is not proof that the computer finished booting.
- Do not print or repeat the Bemfa UID in the response.
- Do not use this skill for status checks, shutdown, restart, or repeated button presses.
