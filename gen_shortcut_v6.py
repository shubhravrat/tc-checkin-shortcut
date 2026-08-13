#!/usr/bin/env python3
"""
Generate TC-Daily-Checkin-v6.shortcut.

v6 changes vs v5:

1. Bugfix carried in from v5's real-world test: `is.workflow.actions.setvariable`
   does NOT implicitly pick up the previous action's output -- it needs an
   explicit WFInput (an ActionOutput ref to the preceding gettext literal) or
   the variable is set to nil, which is why the first v5 build produced an
   effectively empty clipboard even though "Copied to Clipboard" still fired.

2. TC Day no longer prompts. It reuses the same Formatted Date output already
   computed for the header, so "TC — Day <n>" now shows today's date instead
   of a manually typed challenge-day count. One less popup per run.

3. After copying to clipboard, the shortcut opens the Fittr app
   (com.squats.fittr) instead of showing the share sheet, so the text is one
   tap + manual paste away inside Fittr's chat. Share action removed.

Everything else (Health Sum for Water/Steps, Yes/No menus for Diet/Exercise/
Cardio, typed Sleep/Stress/Supplements) is unchanged from v5.
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
        "OutputName": output_name,
        "OutputUUID": output_uuid,
        "Type": "ActionOutput",
    }


def variable_ref(variable_name):
    return {
        "Type": "Variable",
        "VariableName": variable_name,
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


def health_metric(sample_type_label):
    """Find Health Samples (today) -> Calculate Statistics (Sum) for one sample type.

    Returns (filter_action, stats_action, stats_uuid) -- stats_uuid is what
    downstream text attachments wire into.
    """
    filter_act = health_filter_action(sample_type_label)
    stats_act = statistics_sum_action()
    stats_uuid = stats_act["WFWorkflowActionParameters"]["UUID"]
    return filter_act, stats_act, stats_uuid


def ask_action(prompt, default):
    act = action(
        "is.workflow.actions.ask",
        {
            "UUID": U(),
            "WFAskActionDefaultAnswer": default,
            "WFAskActionPrompt": prompt,
            "WFInputType": "Text",
        },
    )
    return act, act["WFWorkflowActionParameters"]["UUID"]


def yes_no_menu(prompt, variable_name, yes_label="Yes ✅", no_label="No ❌"):
    """Choose from Menu: two tap options, each branch Sets Variable `variable_name`.

    Returns the full ordered list of menu-block actions to splice into the
    workflow (menu def, one gettext+setvariable pair per case, end menu).
    """
    group_id = U()
    items = [yes_label, no_label]

    menu_def = action(
        "is.workflow.actions.choosefrommenu",
        {
            "UUID": U(),
            "GroupingIdentifier": group_id,
            "WFControlFlowMode": 0,
            "WFMenuPrompt": prompt,
            "WFMenuItems": items,
        },
    )

    actions = [menu_def]
    for label in items:
        case_act = action(
            "is.workflow.actions.choosefrommenu",
            {
                "UUID": U(),
                "GroupingIdentifier": group_id,
                "WFControlFlowMode": 1,
                "WFMenuItemTitle": label,
            },
        )
        literal_act = action(
            "is.workflow.actions.gettext",
            {"UUID": U(), "WFTextActionText": label},
        )
        literal_uuid = literal_act["WFWorkflowActionParameters"]["UUID"]
        setvar_act = action(
            "is.workflow.actions.setvariable",
            {
                "UUID": U(),
                "WFVariableName": variable_name,
                # Set Variable does NOT implicitly pick up the previous
                # action's output -- it needs an explicit WFInput or the
                # variable is set to nil.
                "WFInput": {
                    "Value": output_ref("Text", literal_uuid),
                    "WFSerializationType": "WFTextTokenAttachment",
                },
            },
        )
        actions += [case_act, literal_act, setvar_act]

    end_act = action(
        "is.workflow.actions.choosefrommenu",
        {"UUID": U(), "GroupingIdentifier": group_id, "WFControlFlowMode": 2},
    )
    actions.append(end_act)
    return actions


FITTR_BUNDLE_ID = "com.squats.fittr"  # App Store bundle ID for "FITTR: Health & Fitness App"


def build():
    date_uuid = U()
    fmt_date_uuid = U()

    date_act = action("is.workflow.actions.date", {"UUID": date_uuid})
    fmt_date_act = action(
        "is.workflow.actions.format.date",
        {"UUID": fmt_date_uuid, "WFDateFormat": "d MMM yyyy", "WFDateFormatStyle": "Custom"},
    )

    diet_menu_actions = yes_no_menu("Diet?", "Diet")
    exercise_menu_actions = yes_no_menu("Exercise?", "Exercise")
    cardio_menu_actions = yes_no_menu("Cardio?", "Cardio")

    water_filter_act, water_stats_act, water_stats_uuid = health_metric("Water")
    steps_filter_act, steps_stats_act, steps_stats_uuid = health_metric("Steps")

    sleep_act, sleep_uuid = ask_action("Sleep (hrs)?", "6")
    stress_act, stress_uuid = ask_action("Stress (x/10)?", "2/10")
    supplements_act, supplements_uuid = ask_action("Supplements?", "Whey, creatine")

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

    # Ready-made attachment refs, one per placeholder in template order.
    # Day reuses the same Formatted Date output as the header -- no separate ask.
    refs_in_order = [
        output_ref("Formatted Date", fmt_date_uuid),
        output_ref("Formatted Date", fmt_date_uuid),
        variable_ref("Diet"),
        variable_ref("Exercise"),
        variable_ref("Cardio"),
        output_ref("Statistics", water_stats_uuid),
        output_ref("Statistics", steps_stats_uuid),
        output_ref("Provided Input", sleep_uuid),
        output_ref("Provided Input", stress_uuid),
        output_ref("Provided Input", supplements_uuid),
    ]

    attachments = {}
    ref_idx = 0
    pos = 0
    for ch in template:
        if ch == PH:
            attachments[f"{{{pos}, 1}}"] = refs_in_order[ref_idx]
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
    openapp_act = action(
        "is.workflow.actions.openapp",
        {"UUID": U(), "WFAppIdentifier": FITTR_BUNDLE_ID},
    )

    actions = [
        date_act,
        fmt_date_act,
        *diet_menu_actions,
        *exercise_menu_actions,
        *cardio_menu_actions,
        water_filter_act,
        water_stats_act,
        steps_filter_act,
        steps_stats_act,
        sleep_act,
        stress_act,
        supplements_act,
        gettext_act,
        setclipboard_act,
        openapp_act,
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

    gettext_actions = [a for a in actions if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.gettext"]
    # The main Text action is the one with a WFTextTokenString dict (attachments);
    # the per-branch menu literals use a bare string.
    main_gettext = next(
        a
        for a in gettext_actions
        if isinstance(a["WFWorkflowActionParameters"]["WFTextActionText"], dict)
    )
    text_uuid = main_gettext["WFWorkflowActionParameters"]["UUID"]
    attachments = main_gettext["WFWorkflowActionParameters"]["WFTextActionText"]["Value"]["attachmentsByRange"]
    assert len(attachments) == 10, f"expected 10 attachments, got {len(attachments)}"

    variable_names_set = {
        a["WFWorkflowActionParameters"]["WFVariableName"]
        for a in actions
        if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.setvariable"
    }
    for rng, ref in attachments.items():
        if ref.get("Type") == "Variable":
            assert ref["VariableName"] in variable_names_set, f"variable ref {ref} at {rng} has no Set Variable writer"
        else:
            assert ref["OutputUUID"] in action_uuids, f"dangling attachment ref {ref} at {rng}"

    # Every Set Variable action must carry an explicit WFInput ref that resolves
    # to a real action UUID -- this is the exact bug that shipped in v5.
    for a in actions:
        if a["WFWorkflowActionIdentifier"] != "is.workflow.actions.setvariable":
            continue
        wf_input = a["WFWorkflowActionParameters"].get("WFInput")
        assert wf_input is not None, f"setvariable {a['WFWorkflowActionParameters']['UUID']} has no WFInput"
        source_uuid = wf_input["Value"]["OutputUUID"]
        assert source_uuid in action_uuids, f"setvariable WFInput references missing action {source_uuid}"

    setclipboard = next(a for a in actions if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.setclipboard")
    # setclipboard has no explicit WFInput here (implicit pipe from the immediately
    # preceding action) -- confirm the Text action is that immediate predecessor.
    idx = actions.index(setclipboard)
    predecessor = actions[idx - 1]
    assert predecessor["WFWorkflowActionParameters"]["UUID"] == text_uuid, (
        "setclipboard's implicit input is not the Text action"
    )

    openapp = next(a for a in actions if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.openapp")
    assert openapp["WFWorkflowActionParameters"]["WFAppIdentifier"] == FITTR_BUNDLE_ID
    assert actions.index(openapp) == idx + 1, "Open App must immediately follow Set Clipboard"

    # Every choosefrommenu block: modes 0/1/1/2 with one shared GroupingIdentifier,
    # WFMenuItemTitle order matches WFMenuItems order.
    menu_actions = [a for a in actions if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.choosefrommenu"]
    assert len(menu_actions) == 12, f"expected 12 choosefrommenu actions (3 groups x 4), got {len(menu_actions)}"
    for i in range(0, len(menu_actions), 4):
        block = menu_actions[i : i + 4]
        gid = block[0]["WFWorkflowActionParameters"]["GroupingIdentifier"]
        modes = [b["WFWorkflowActionParameters"]["WFControlFlowMode"] for b in block]
        assert modes == [0, 1, 1, 2], f"menu block at index {i} has wrong mode sequence {modes}"
        assert all(b["WFWorkflowActionParameters"]["GroupingIdentifier"] == gid for b in block), (
            f"menu block at index {i} has mismatched GroupingIdentifier"
        )
        items = block[0]["WFWorkflowActionParameters"]["WFMenuItems"]
        titles = [b["WFWorkflowActionParameters"]["WFMenuItemTitle"] for b in block[1:3]]
        assert items == titles, f"menu block at index {i}: WFMenuItems {items} != case titles {titles}"

    print(f"OK: {path} -> {len(actions)} actions, {len(attachments)} attachments, all refs resolve")


if __name__ == "__main__":
    wf = build()
    out_path = "TC-Daily-Checkin-v6.shortcut"
    with open(out_path, "wb") as f:
        plistlib.dump(wf, f, fmt=plistlib.FMT_BINARY)
    validate(out_path, expected_action_count=36)
