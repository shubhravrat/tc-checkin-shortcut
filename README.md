# TC Daily Check-in Shortcut

An iOS Shortcut that prompts for a daily check-in (diet, exercise, cardio,
water, steps, sleep, stress, supplements), assembles the answers into a
formatted text block dated and day-numbered off today's date, copies it to
the clipboard, and opens the Fittr app so it can be pasted into its chat.

## Files

| File | Description |
| --- | --- |
| `TC-Daily-Checkin-v6-signed.shortcut` | v6, current. TC Day auto-fills from today's date (no popup); Diet/Exercise/Cardio are tap-to-choose menus; Steps/Water pulled live from Apple Health; copies to clipboard then opens Fittr instead of the share sheet. Signed, import this one. |
| `TC-Daily-Checkin-v6.shortcut` | v6 unsigned. iOS refuses to import it. |
| `gen_shortcut_v6.py` | Generator for v6. |
| `TC-Daily-Checkin-v5-signed.shortcut` | v5, legacy. Diet/Exercise/Cardio tap-to-choose menus; Day/Stress/Supplements typed; Steps/Water from Health; ends with the share sheet. |
| `TC-Daily-Checkin-v5.shortcut` | v5 unsigned. |
| `gen_shortcut_v5.py` | Generator for v5. |
| `TC-Daily-Checkin-v3-signed.shortcut` | v3, legacy. Steps and Water pulled live from Apple Health; Diet/Exercise/Cardio still typed. |
| `TC-Daily-Checkin-v3.shortcut` | v3 unsigned. |
| `gen_shortcut_v3.py` | Generator for v3. |
| `TC-Daily-Checkin-signed.shortcut` | v2, legacy. All fields asked manually, including Steps/Water. |
| `TC-Daily-Checkin.shortcut` | v2 unsigned. |

## Install on iPhone

1. Open this link in Safari on the iPhone:
   https://github.com/shubhravrat/tc-checkin-shortcut/raw/main/TC-Daily-Checkin-v6-signed.shortcut
2. The file downloads to Files.
3. Tap the download, then **Add Shortcut**.
4. First run will prompt for Health read permission (Steps, Water) and
   permission to open the Fittr app. Allow both.

## Re-signing

If the shortcut is edited, re-sign it on a Mac before importing:

```
shortcuts sign --mode anyone \
  --input TC-Daily-Checkin-v6.shortcut \
  --output TC-Daily-Checkin-v6-signed.shortcut
```
