# TC Daily Check-in Shortcut

An iOS Shortcut that prompts for a daily check-in (TC day number, diet, exercise,
cardio, water, steps, sleep, stress, supplements), assembles the answers into a
formatted text block with the current date, copies it to the clipboard, and opens
the share sheet.

## Files

| File | Description |
| --- | --- |
| `TC-Daily-Checkin-v3-signed.shortcut` | v3, current. Steps and Water pulled live from Apple Health instead of asked. Signed, import this one. |
| `TC-Daily-Checkin-v3.shortcut` | v3 unsigned. iOS refuses to import it. |
| `gen_shortcut_v3.py` | Generator for v3. |
| `TC-Daily-Checkin-signed.shortcut` | v2, legacy. All fields asked manually, including Steps/Water. |
| `TC-Daily-Checkin.shortcut` | v2 unsigned. |

## Install on iPhone

1. Open this link in Safari on the iPhone:
   https://github.com/shubhravrat/tc-checkin-shortcut/raw/main/TC-Daily-Checkin-v3-signed.shortcut
2. The file downloads to Files.
3. Tap the download, then **Add Shortcut**.
4. First run will prompt for Health read permission (Steps, Water). Allow it.

## Re-signing

If the shortcut is edited, re-sign it on a Mac before importing:

```
shortcuts sign --mode anyone \
  --input TC-Daily-Checkin-v3.shortcut \
  --output TC-Daily-Checkin-v3-signed.shortcut
```
