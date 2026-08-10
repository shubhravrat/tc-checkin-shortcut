# TC Daily Check-in Shortcut

An iOS Shortcut that prompts for a daily check-in (TC day number, diet, exercise,
cardio, water, steps, sleep, stress, supplements), assembles the answers into a
formatted text block with the current date, copies it to the clipboard, and opens
the share sheet.

## Files

| File | Description |
| --- | --- |
| `TC-Daily-Checkin-signed.shortcut` | Signed with `shortcuts sign --mode anyone`. Import this one. |
| `TC-Daily-Checkin.shortcut` | Unsigned original. iOS refuses to import it. |

## Install on iPhone

1. Open this link in Safari on the iPhone:
   https://github.com/shubhravrat/tc-checkin-shortcut/raw/main/TC-Daily-Checkin-signed.shortcut
2. The file downloads to Files.
3. Tap the download, then **Add Shortcut**.

## Re-signing

If the shortcut is edited, re-sign it on a Mac before importing:

```
shortcuts sign --mode anyone \
  --input TC-Daily-Checkin.shortcut \
  --output TC-Daily-Checkin-signed.shortcut
```
