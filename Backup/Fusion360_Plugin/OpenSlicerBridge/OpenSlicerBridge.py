# -*- coding: utf-8 -*-
# OpenSlicer Studio — Autodesk Fusion 360 Live Bridge Add-In
# Exports active design or selected body to a watched .STL file with automatic [ProjectName]-[BodyName].stl naming.

import adsk.core
import adsk.fusion
import os
import re
import json
import traceback

handlers = []
CMD_ID = 'OpenSlicerBridge_SendLiveSTL'
CMD_NAME = 'Send to OpenSlicer (Live STL)'
CMD_DESC = 'Exports active body/component to [Project]-[Body].stl in the chosen folder for live slicing in OpenSlicer Studio.'
PANEL_ID = 'SolidMakePanel'

CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bridge_config.json')
DEFAULT_EXPORT_FOLDER = r'd:\Projeler\Open Slicer'


def sanitize_filename(name):
    if not name:
        return ''
    # Strip extension if already present
    clean = re.sub(r'\.(stl|obj|3mf|f3d)$', '', name, flags=re.I)
    # Strip Autodesk version suffix like ' v1', ' v2', ' v10'
    clean = re.sub(r'\s+v\d+$', '', clean, flags=re.I)
    # Replace characters not allowed in filenames on Windows
    clean = re.sub(r'[\\/*?:"<>|]', '_', clean)
    clean = re.sub(r'\s+', '_', clean).strip('_')
    return clean


def compute_export_filename(target_entity=None):
    app = adsk.core.Application.get()
    doc_name = ''
    try:
        if app.activeDocument:
            doc_name = sanitize_filename(app.activeDocument.name)
    except Exception:
        pass

    body_name = ''
    if target_entity:
        try:
            body_name = sanitize_filename(target_entity.name)
        except Exception:
            pass

    if doc_name and body_name:
        filename = '{}-{}.stl'.format(doc_name, body_name)
    elif body_name:
        filename = '{}.stl'.format(body_name)
    elif doc_name:
        filename = '{}.stl'.format(doc_name)
    else:
        filename = 'Model.stl'

    return filename


def load_config():
    cfg = {
        'export_folder': DEFAULT_EXPORT_FOLDER,
        'auto_sync_on_save': True
    }
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cfg.update(data)
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def export_active_to_stl(export_folder, target_entity=None):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        return False, 'No active Fusion 360 Design.'

    if target_entity is None:
        target_entity = design.rootComponent

    if not export_folder or not os.path.exists(export_folder):
        try:
            os.makedirs(export_folder, exist_ok=True)
        except Exception:
            export_folder = DEFAULT_EXPORT_FOLDER
            os.makedirs(export_folder, exist_ok=True)

    filename = compute_export_filename(target_entity)
    stl_path = os.path.join(export_folder, filename)

    export_mgr = design.exportManager
    stl_opts = export_mgr.createSTLExportOptions(target_entity, stl_path)
    stl_opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    stl_opts.isBinaryFormat = True
    ok = export_mgr.execute(stl_opts)
    return ok, stl_path


class SendCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            cfg = load_config()

            sel_input = inputs.addSelectionInput(
                'bodySelect',
                'Body / Component (Optional)',
                'Select a specific body/component, or leave empty to export the whole design'
            )
            sel_input.addSelectionFilter('Bodies')
            sel_input.addSelectionFilter('Occurrences')
            sel_input.setSelectionLimits(0, 1)

            folder_input = inputs.addStringValueInput(
                'exportFolder',
                'Export Folder',
                cfg.get('export_folder', DEFAULT_EXPORT_FOLDER)
            )

            preview_name = compute_export_filename(None)
            inputs.addTextBoxCommandInput(
                'namePreview',
                'File Name Format',
                '<b>{}</b><br><small>Rule: [ProjectName]-[BodyName].stl</small>'.format(preview_name),
                2,
                True
            )

            inputs.addBoolValueInput(
                'autoSyncSave',
                'Auto-Update STL on Fusion Save (Ctrl+S)',
                True,
                '',
                bool(cfg.get('auto_sync_on_save', True))
            )

            on_input_changed = SendCommandInputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            handlers.append(on_input_changed)

            on_exec = SendCommandExecuteHandler()
            cmd.execute.add(on_exec)
            handlers.append(on_exec)
        except Exception:
            app = adsk.core.Application.get()
            if app and app.userInterface:
                app.userInterface.messageBox('OpenSlicer Bridge Error:\n{}'.format(traceback.format_exc()))


class SendCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs
            sel_input = adsk.core.SelectionCommandInput.cast(inputs.itemById('bodySelect'))
            preview_box = adsk.core.TextBoxCommandInput.cast(inputs.itemById('namePreview'))

            target_ent = None
            if sel_input and sel_input.selectionCount > 0:
                target_ent = sel_input.selection(0).entity

            if preview_box:
                fname = compute_export_filename(target_ent)
                preview_box.formattedText = '<b>{}</b><br><small>Rule: [ProjectName]-[BodyName].stl</small>'.format(fname)
        except Exception:
            pass


class SendCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            sel_input = adsk.core.SelectionCommandInput.cast(inputs.itemById('bodySelect'))
            folder_input = adsk.core.StringValueCommandInput.cast(inputs.itemById('exportFolder'))
            auto_input = adsk.core.BoolValueCommandInput.cast(inputs.itemById('autoSyncSave'))

            export_folder = folder_input.value.strip() if folder_input else DEFAULT_EXPORT_FOLDER

            target_ent = None
            if sel_input and sel_input.selectionCount > 0:
                target_ent = sel_input.selection(0).entity

            cfg = {
                'export_folder': export_folder,
                'auto_sync_on_save': bool(auto_input.value) if auto_input else True
            }
            save_config(cfg)

            ok, stl_path = export_active_to_stl(export_folder, target_ent)
            if ok:
                app = adsk.core.Application.get()
                if app and app.userInterface:
                    app.userInterface.messageBox('Exported for OpenSlicer:\n\n{}'.format(stl_path))
        except Exception:
            app = adsk.core.Application.get()
            if app and app.userInterface:
                app.userInterface.messageBox('OpenSlicer Export Error:\n{}'.format(traceback.format_exc()))


class DocumentSavedAutoSyncHandler(adsk.core.DocumentEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cfg = load_config()
            if cfg.get('auto_sync_on_save', True):
                export_folder = cfg.get('export_folder', DEFAULT_EXPORT_FOLDER)
                export_active_to_stl(export_folder, None)
        except Exception:
            pass


def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_DESC)

        on_created = SendCommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        handlers.append(on_created)

        panel = ui.allToolbarPanels.itemById(PANEL_ID)
        if panel:
            ctrl = panel.controls.itemById(CMD_ID)
            if not ctrl:
                ctrl = panel.controls.addCommand(cmd_def)
                ctrl.isPromoted = True
                ctrl.isPromotedByDefault = True

        on_doc_saved = DocumentSavedAutoSyncHandler()
        app.documentSaved.add(on_doc_saved)
        handlers.append(on_doc_saved)
    except Exception:
        app = adsk.core.Application.get()
        if app and app.userInterface:
            app.userInterface.messageBox('OpenSlicer Bridge Startup Error:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        panel = ui.allToolbarPanels.itemById(PANEL_ID)
        if panel:
            ctrl = panel.controls.itemById(CMD_ID)
            if ctrl:
                ctrl.deleteMe()
        cmd_def = ui.commandDefinitions.itemById(CMD_ID)
        if cmd_def:
            cmd_def.deleteMe()
    except Exception:
        pass
