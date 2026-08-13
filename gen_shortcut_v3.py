#!/usr/bin/env python3
"""
Generate TC-Daily-Checkin-v3.shortcut.

v3 change vs v2: Steps and Water are pulled live from Apple Health
(Find Health Samples -> Calculate Statistics -> Sum) instead of ask-for-input
prompts. All other prompts (TC day, Diet, Exercise, Cardio, Sleep, Stress,
Supplements) are unchanged ask actions.

Health action serialization reference (WFContentPredicateTableTemplate shape,
Operator 4 = "is" on Type, Operator 1002 = "is today" on Start Date) verified
against real iOS-exported .shortcut XML surfaced via GitHub code search
(viticci/shortcuts-playground-plugin, HEALTHKIT.md / healthkit-ios26.2-reference.json).
Do NOT use a top-level WFHealthQuantitySampleType key -- iOS imports it as an
inert field; the sample type lives inside the Type filter row's Enumeration value.
"""
import plistlib
import uuid


def U():
    return str(uuid.uuid4()).upper()


def action(identifier, params):
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": params,
    }


def output_ref(output_name, output_uuid):
    return {
        "Value": {
            "OutputName": output_name,
            "OutputUUID": output_uuid,
            "Type": "ActionOutput",
        },
        "WFSerializationType": "WFTextTokenAttachment",
    }


def health_filter_action(sample_type_label):
    """Find Health Samples: Type is <label> AND Start Date is today."""
    return action(
        "is.workflow.actions.filter.health.quantity",
        {
            "UUID": U(),
            "WFContentItemFilter": {
                "Value": {
                    "WFActionParameterFilterPrefix": 1,
                    "WFContentPredicateBoundedDate": False,
                    "WFActionParameterFilterTemplates": [
                        {
                            "Bounded": True,
                            "Operator": 4,
                            "Property": "Type",
                            "Removable": False,
                            "Values": {
                                "Enumeration": {
                                    "Value": sample_type_label,
                                    "WFSerializationType": "WFStringSubstitutableState",
                                }
                            },
                        },
                        {
                            "Bounded": True,
                            "Operator": 1002,
                            "Property": "Start Date",
                            "Removable": False,
                            "Values": {
                                "Number": "7",
                                "Unit": 16,
                            },
                        },
                    ],
                },
                "WFSerializationType": "WFContentPredicateTableTemplate",
            },
        },
    )


def statistics_sum_action():
    return action(
        "is.workflow.actions.statistics",
        {
            "UUID": U(),
            "WFStatisticsOperation": "Sum",
        },
    )


def ask_action(prompt, default, uid, input_type="Text"):
    return action(
        "is.workflow.actions.ask",
        {
            "UUID": uid,
            "WFAskActionDefaultAnswer": default,
            "WFAskActionPrompt": prompt,
            "WFInputType": input_type,
        },
    )


def build():
    date_uuid = U()
    fmt_date_uuid = U()

    tc_day_uuid = U()
    diet_uuid = U()
    exercise_uuid = U()
    cardio_uuid = U()
    sleep_uuid = U()
    stress_uuid = U()
    supplements_uuid = U()

    date_act = action("is.workflow.actions.date", {"UUID": date_uuid})
    fmt_date_act = action(
        "is.workflow.actions.format.date",
        {"UUID": fmt_date_uuid, "WFDateFormat": "d MMM yyyy", "WFDateFormatStyle": "Custom"},
    )

    tc_day_act = ask_action("TC Day number?", "17", tc_day_uuid)
    diet_act = ask_action("Diet?", "Yes ✅", diet_uuid)
    exercise_act = ask_action("Exercise?", "Yes ✅", exercise_uuid)
    cardio_act = ask_action("Cardio?", "No ❌", cardio_uuid)

    water_filter_act = health_filter_action("Water")
    water_filter_uuid = water_filter_act["WFWorkflowActionParameters"]["UUID"]
    water_stats_act = statistics_sum_action()
    water_stats_uuid = water_stats_act["WFWorkflowActionParameters"]["UUID"]

    steps_filter_act = health_filter_action("Steps")
    steps_filter_uuid = steps_filter_act["WFWorkflowActionParameters"]["UUID"]
    steps_stats_act = statistics_sum_action()
    steps_stats_uuid = steps_stats_act["WFWorkflowActionParameters"]["UUID"]

    sleep_act = ask_action("Sleep (hrs)?", "6", sleep_uuid)
    stress_act = ask_action("Stress (x/10)?", "2/10", stress_uuid)
    supplements_act = ask_action("Supplements?", "Whey, creatine", supplements_uuid)

    # ---- text template with UTF-16 offset computation ----
    PH = "￼"  # Object Replacement Character used by Shortcuts for attachments
    template = (
        f"\U0001f5d3️ {PH}  |  TC — Day {PH}\n"
        f"━━━━━━━━━━━━━━\n"
        f"\U0001f957 Diet · {PH}\n"
        f"\U0001f3cb️ Exercise · {PH}\n"
        f"\U0001f3c3 Cardio · {PH}\n"
        f"\U0001f4a7 Water · {PH} L\n"
        f"\U0001f45f Steps · {PH}\n"
        f"\U0001f634 Sleep · {PH} hrs\n"
        f"\U0001f9d8 Stress · {PH}\n"
        f"\U0001f48a Supplements · {PH}"
    )

    refs_in_order = [
        ("Formatted Date", fmt_date_uuid),
        ("Provided Input", tc_day_uuid),
        ("Provided Input", diet_uuid),
        ("Provided Input", exercise_uuid),
        ("Provided Input", cardio_uuid),
        ("Statistics", water_stats_uuid),
        ("Statistics", steps_stats_uuid),
        ("Provided Input", sleep_uuid),
        ("Provided Input", stress_uuid),
        ("Provided Input", supplements_uuid),
    ]

    attachments = {}
    ref_idx = 0
    pos = 0
    for ch in template:
        if ch == PH:
            out_name, out_uuid = refs_in_order[ref_idx]
            attachments[f"{{{pos}, 1}}"] = {
                "OutputName": out_name,
                "OutputUUID": out_uuid,
                "Type": "ActionOutput",
            }
            ref_idx += 1
        pos += 2 if ord(ch) > 0xFFFF else 1
    assert ref_idx == len(refs_in_order), "placeholder/reference count mismatch"

    gettext_uuid = U()
    gettext_act = action(
        "is.workflow.actions.gettext",
        {
            "UUID": gettext_uuid,
            "WFTextActionText": {
                "Value": {
                    "attachmentsByRange": attachments,
                    "string": template,
                },
                "WFSerializationType": "WFTextTokenString",
            },
        },
    )

    setclipboard_act = action("is.workflow.actions.setclipboard", {"UUID": U()})
    share_act = action("is.workflow.actions.share", {"UUID": U()})

    actions = [
        date_act,
        fmt_date_act,
        tc_day_act,
        diet_act,
        exercise_act,
        cardio_act,
        water_filter_act,
        water_stats_act,
        steps_filter_act,
        steps_stats_act,
        sleep_act,
        stress_act,
        supplements_act,
        gettext_act,
        setclipboard_act,
        share_act,
    ]

    workflow = {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "2605.0.5",
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 431817727,
            "WFWorkflowIconGlyphNumber": 61440,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": ["WFStringContentItem"],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowTypes": [],
    }
    return workflow


def validate(path, expected_action_count):
    with open(path, "rb") as f:
        d = plistlib.load(f)
    actions = d["WFWorkflowActions"]
    assert len(actions) == expected_action_count, f"expected {expected_action_count} actions, got {len(actions)}"

    action_uuids = set()
    for a in actions:
        p = a["WFWorkflowActionParameters"]
        if "UUID" in p:
            action_uuids.add(p["UUID"])

    gettext = next(a for a in actions if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext")
    attachments = gettext["WFWorkflowActionParameters"]["WFTextActionText"]["Value"]["attachmentsByRange"]
    assert len(attachments) == 10, f"expected 10 attachments, got {len(attachments)}"
    for rng, ref in attachments.items():
        assert ref["OutputUUID"] in action_uuids, f"dangling attachment ref {ref} at {rng}"

    print(f"OK: {path} -> {len(actions)} actions, {len(attachments)} attachments, all UUIDs resolve")


if __name__ == "__main__":
    wf = build()
    out_path = "TC-Daily-Checkin-v3.shortcut"
    with open(out_path, "wb") as f:
        plistlib.dump(wf, f, fmt=plistlib.FMT_BINARY)
    validate(out_path, expected_action_count=16)
