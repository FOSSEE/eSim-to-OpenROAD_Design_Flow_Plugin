#!/usr/bin/envpython3

# =========================================================================
#      FILE:     OpenROAD.py
#
#     USAGE: ---
#
#   DESCRIPTION: This file is used setup of orfs
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Rishabh Jain, 2r10j5@gmail.com
#    MAINTAINED: Sumanto Kar, sumantokar@iitb.ac.in
#  ORGANIZATION: eSim Team at FOSSEE, IIT Bombay
#       CREATED: Monday 27 July 2026
# =========================================================================

import os
import subprocess
import sys
import traceback
from datetime import datetime

from PyQt5 import QtCore, QtWidgets, QtGui

from configuration.Appconfig import Appconfig
from maker.OpenROAD import OpenROADFlow


class OpenROADWorker(QtCore.QObject):

    progressChanged = QtCore.pyqtSignal(int)
    statusChanged = QtCore.pyqtSignal(str)
    logMessage = QtCore.pyqtSignal(str)
    flowCompleted = QtCore.pyqtSignal(dict)
    flowFailed = QtCore.pyqtSignal(str)

    def __init__(self, design_name, verilog_file, platform, cir_file=None):
        super().__init__()
        self.design_name = design_name
        self.verilog_file = verilog_file
        self.platform = platform
        self.cir_file = cir_file
        self._cancel = False
        self._process = None
        self.project_dir = os.path.dirname(verilog_file)

    def cancel(self):
        self._cancel = True
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass

    def _ts(self, level, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {level}: {msg}"

    def _emit_log(self, level, msg):
        self.logMessage.emit(self._ts(level, msg))

    @QtCore.pyqtSlot()
    def run(self):
        try:
            if self.cir_file and self.cir_file.endswith(".cir.out"):
                self._emit_log("INFO", "Starting Netlist to RTL conversion")
                self.statusChanged.emit("Converting netlist to RTL...")
                self.progressChanged.emit(5)

                netlist_script = os.path.join(
                    os.path.dirname(__file__), "..", "maker", "netlist2rtl.py"
                )
                netlist_script = os.path.normpath(netlist_script)
                cmd = [sys.executable, netlist_script, self.cir_file]
                self._process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in self._process.stdout:
                    if self._cancel:
                        self._process.terminate()
                        self.flowFailed.emit("Flow cancelled by user")
                        return
                    stripped = line.strip()
                    if stripped:
                        self._emit_log("INFO", stripped)
                self._process.wait()

                if self._cancel:
                    self.flowFailed.emit("Flow cancelled by user")
                    return
                if self._process.returncode != 0:
                    self.flowFailed.emit("Netlist to RTL conversion failed")
                    return

                proj_dir = os.path.dirname(self.cir_file)
                self.design_name = os.path.basename(
                    self.cir_file
                ).replace(".cir.out", "")
                self.verilog_file = os.path.join(
                    proj_dir, self.design_name + ".v"
                )
                self.project_dir = proj_dir

                if not os.path.exists(self.verilog_file):
                    self.flowFailed.emit(
                        f"Generated Verilog not found: {self.verilog_file}"
                    )
                    return

                self._emit_log("SUCCESS", "RTL Generated")
                self.statusChanged.emit("RTL generated")
                self.progressChanged.emit(15)

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            flow = OpenROADFlow(
                self.design_name, self.verilog_file, self.platform
            )
            self.project_dir = flow.project_dir

            self._emit_log("INFO", "Checking ORFS installation")
            self.statusChanged.emit("Checking ORFS...")
            self.progressChanged.emit(20)
            flow.check_orfs()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            self._emit_log("INFO", "Creating design structure")
            self.statusChanged.emit("Creating design structure...")
            self.progressChanged.emit(30)
            flow.create_structure()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            self._emit_log("INFO", "Copying Verilog file")
            self.statusChanged.emit("Copying Verilog...")
            self.progressChanged.emit(40)
            flow.copy_verilog()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            self._emit_log("INFO", "Generating SDC constraints")
            self.statusChanged.emit("Generating constraints...")
            self.progressChanged.emit(50)
            flow.generate_sdc()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            self._emit_log("INFO", "Generating config.mk")
            self.statusChanged.emit("Generating configuration...")
            self.progressChanged.emit(60)
            flow.generate_config()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return

            self._emit_log("INFO", "Starting OpenROAD flow")
            self.statusChanged.emit("Running Synthesis...")
            self.progressChanged.emit(65)

            cmd = [
                "make",
                f"DESIGN_CONFIG=./designs/{self.platform}/{self.design_name}/config.mk",
            ]
            self._process = subprocess.Popen(
                cmd,
                cwd=flow.flow_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            stage_map = {
                "synthesis": "Running Synthesis...",
                "floorplan": "Floorplanning...",
                "placement": "Placement...",
                "cts": "CTS...",
                "routing": "Routing...",
                "gds": "Generating GDS...",
            }
            progress_range = 90 - 65
            line_count = 0

            for line in self._process.stdout:
                if self._cancel:
                    self._process.terminate()
                    self.flowFailed.emit("Flow cancelled by user")
                    return
                stripped = line.strip()
                if stripped:
                    self._emit_log("INFO", stripped)
                line_lower = line.lower()
                for key, stage in stage_map.items():
                    if key in line_lower:
                        self.statusChanged.emit(stage)
                if line_count % 50 == 0:
                    p = min(
                        65 + int((line_count / 5000.0) * progress_range), 89
                    )
                    self.progressChanged.emit(p)
                line_count += 1

            self._process.wait()

            if self._cancel:
                self.flowFailed.emit("Flow cancelled by user")
                return
            if self._process.returncode != 0:
                self.flowFailed.emit("OpenROAD flow failed")
                return

            self._process = None

            self._emit_log("INFO", "Collecting outputs")
            self.statusChanged.emit("Collecting outputs...")
            self.progressChanged.emit(92)
            flow.collect_outputs()

            outputs = {
                "gds": os.path.join(
                    self.project_dir, self.design_name + ".gds"
                ),
                "def": os.path.join(
                    self.project_dir, self.design_name + ".def"
                ),
                "v": os.path.join(
                    self.project_dir, self.design_name + ".v"
                ),
                "sdc": os.path.join(
                    self.project_dir, self.design_name + ".sdc"
                ),
                "spef": os.path.join(
                    self.project_dir, self.design_name + ".spef"
                ),
                "logs": os.path.join(self.project_dir, "logs"),
                "reports": os.path.join(self.project_dir, "reports"),
                "project_dir": self.project_dir,
            }

            self._emit_log("SUCCESS", "GDS Generated")
            self.statusChanged.emit("Completed")
            self.progressChanged.emit(100)
            self.flowCompleted.emit(outputs)

        except FileNotFoundError as e:
            self._emit_log("ERROR", str(e))
            self.flowFailed.emit(str(e))
        except RuntimeError as e:
            self._emit_log("ERROR", str(e))
            self.flowFailed.emit(str(e))
        except Exception as e:
            self._emit_log("ERROR", f"{e}\n{traceback.format_exc()}")
            self.flowFailed.emit(str(e))

    def __del__(self):
        self._cancel = True
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass


class OpenROADWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.obj_appconfig = Appconfig()
        self.worker = None
        self.thread = None
        self.flow_running = False
        self._outputs = None
        self._init_ui()
        self._update_project_info()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        project_group = QtWidgets.QGroupBox("Current Project")
        project_layout = QtWidgets.QFormLayout()
        project_layout.setSpacing(4)
        self.project_name_label = QtWidgets.QLabel("No project selected")
        self.project_name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.project_folder_label = QtWidgets.QLabel("")
        self.project_folder_label.setWordWrap(True)
        self.platform_combo = QtWidgets.QComboBox()
        self.platform_combo.addItems(["sky130hd", "sky130hs", "asap7"])
        project_layout.addRow("Name:", self.project_name_label)
        project_layout.addRow("Folder:", self.project_folder_label)
        project_layout.addRow("Platform:", self.platform_combo)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        input_group = QtWidgets.QGroupBox("Input File")
        input_layout = QtWidgets.QVBoxLayout()
        input_layout.setSpacing(4)
        browse_layout = QtWidgets.QHBoxLayout()
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("Browse for .cir.out or .v file...")
        self.browse_btn = QtWidgets.QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse_file)
        browse_layout.addWidget(self.file_path_edit)
        browse_layout.addWidget(self.browse_btn)
        input_layout.addLayout(browse_layout)
        self.file_type_label = QtWidgets.QLabel("")
        self.file_type_label.setStyleSheet(
            "color: #2e7d32; font-weight: bold; font-size: 11px;"
        )
        input_layout.addWidget(self.file_type_label)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        flow_group = QtWidgets.QGroupBox("Flow Progress")
        flow_layout = QtWidgets.QVBoxLayout()
        flow_layout.setSpacing(4)
        self.stage_label = QtWidgets.QLabel("Ready")
        self.stage_label.setStyleSheet("font-weight: bold; color: #555;")
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        flow_layout.addWidget(self.stage_label)
        flow_layout.addWidget(self.progress_bar)
        flow_group.setLayout(flow_layout)
        layout.addWidget(flow_group)

        console_group = QtWidgets.QGroupBox("Console")
        console_layout = QtWidgets.QVBoxLayout()
        console_layout.setContentsMargins(2, 2, 2, 2)
        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QtGui.QFont("Courier New", 9))
        self.console.setStyleSheet(
            "QTextEdit { background-color: #1e1e1e; color: #d4d4d4;"
            " border: 1px solid #555; }"
        )
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        outputs_group = QtWidgets.QGroupBox("Generated Outputs")
        outputs_layout = QtWidgets.QGridLayout()
        outputs_layout.setSpacing(4)
        self.output_buttons = {}
        output_defs = [
            ("Open RTL", "v"),
            ("Open DEF", "def"),
            ("Open GDS", "gds"),
            ("Open SDC", "sdc"),
            ("Open SPEF", "spef"),
            ("Open Logs", "logs"),
            ("Open Reports", "reports"),
            ("Open Project Folder", "project"),
        ]
        for i, (label, key) in enumerate(output_defs):
            btn = QtWidgets.QPushButton(label)
            btn.setEnabled(False)
            btn.clicked.connect(lambda checked, k=key: self._open_output(k))
            self.output_buttons[key] = btn
            outputs_layout.addWidget(btn, i // 4, i % 4)
        outputs_group.setLayout(outputs_layout)
        layout.addWidget(outputs_group)

        tools_layout = QtWidgets.QHBoxLayout()
        tools_layout.setSpacing(6)
        self.run_btn = QtWidgets.QPushButton(" Run OpenROAD")
        self.run_btn.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        )
        self.run_btn.setMinimumHeight(32)
        self.run_btn.clicked.connect(self._run_flow)
        self.run_btn.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white;"
            " font-weight: bold; border-radius: 4px; padding: 6px 16px; }"
            " QPushButton:hover { background-color: #1b5e20; }"
            " QPushButton:disabled { background-color: #ccc; color: #888; }"
        )

        self.cancel_btn = QtWidgets.QPushButton(" Cancel")
        self.cancel_btn.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop)
        )
        self.cancel_btn.setMinimumHeight(32)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_flow)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background-color: #c62828; color: white;"
            " font-weight: bold; border-radius: 4px; padding: 6px 16px; }"
            " QPushButton:hover { background-color: #b71c1c; }"
            " QPushButton:disabled { background-color: #ccc; color: #888; }"
        )

        self.open_gui_btn = QtWidgets.QPushButton(" Open GUI")
        self.open_gui_btn.setMinimumHeight(32)
        self.open_gui_btn.setEnabled(False)
        self.open_gui_btn.clicked.connect(self._open_gui)
        self.open_gui_btn.setStyleSheet(
            "QPushButton { background-color: #1565c0; color: white;"
            " border-radius: 4px; padding: 6px 16px; }"
            " QPushButton:hover { background-color: #0d47a1; }"
            " QPushButton:disabled { background-color: #ccc; color: #888; }"
        )

        self.open_klayout_btn = QtWidgets.QPushButton(" KLayout")
        self.open_klayout_btn.setMinimumHeight(32)
        self.open_klayout_btn.setEnabled(False)
        self.open_klayout_btn.clicked.connect(self._open_klayout)
        self.open_klayout_btn.setStyleSheet(
            "QPushButton { background-color: #6a1b9a; color: white;"
            " border-radius: 4px; padding: 6px 16px; }"
            " QPushButton:hover { background-color: #4a148c; }"
            " QPushButton:disabled { background-color: #ccc; color: #888; }"
        )

        self.clear_btn = QtWidgets.QPushButton(" Clear")
        self.clear_btn.setMinimumHeight(32)
        self.clear_btn.clicked.connect(self.console.clear)
        self.clear_btn.setStyleSheet(
            "QPushButton { background-color: #546e7a; color: white;"
            " border-radius: 4px; padding: 6px 16px; }"
            " QPushButton:hover { background-color: #37474f; }"
        )

        tools_layout.addWidget(self.run_btn)
        tools_layout.addWidget(self.cancel_btn)
        tools_layout.addWidget(self.open_gui_btn)
        tools_layout.addWidget(self.open_klayout_btn)
        tools_layout.addStretch()
        tools_layout.addWidget(self.clear_btn)
        layout.addLayout(tools_layout)

        self.setLayout(layout)

    def _update_project_info(self):
        proj = self.obj_appconfig.current_project
        proj_dir = proj.get("ProjectName")
        if proj_dir:
            self.project_name_label.setText(os.path.basename(proj_dir))
            self.project_folder_label.setText(proj_dir)
        else:
            self.project_name_label.setText("No project selected")
            self.project_folder_label.setText("")

    def _browse_file(self):
        proj = self.obj_appconfig.current_project
        proj_dir = proj.get("ProjectName")
        if not proj_dir:
            QtWidgets.QMessageBox.warning(
                self, "No Project",
                "Please open or create a project first."
            )
            return
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Input File",
            proj_dir,
            "Supported Files (*.cir.out *.v);;Ngspice Netlist (*.cir.out);;Verilog (*.v)",
        )
        if not file_path:
            return
        self.file_path_edit.setText(file_path)
        if file_path.endswith(".cir.out"):
            self.file_type_label.setText("\u2713 Ngspice Netlist")
            self.file_type_label.setStyleSheet(
                "color: #2e7d32; font-weight: bold; font-size: 11px;"
            )
        elif file_path.endswith(".v"):
            self.file_type_label.setText("\u2713 Verilog RTL")
            self.file_type_label.setStyleSheet(
                "color: #1565c0; font-weight: bold; font-size: 11px;"
            )
        else:
            self.file_type_label.setText("")

    def _append_log(self, msg):
        color_map = {
            "ERROR": "#f44336",
            "WARNING": "#ff9800",
            "SUCCESS": "#4caf50",
            "INFO": "#2196f3",
        }
        color = "#d4d4d4"
        for key, c in color_map.items():
            if key in msg:
                color = c
                break
        self.console.append(f'<span style="color:{color}">{msg}</span>')

    def _set_ui_busy(self, busy):
        self.flow_running = busy
        self.run_btn.setEnabled(not busy)
        self.cancel_btn.setEnabled(busy)
        self.browse_btn.setEnabled(not busy)

    def _run_flow(self):
        proj = self.obj_appconfig.current_project
        proj_dir = proj.get("ProjectName")
        if not proj_dir:
            QtWidgets.QMessageBox.warning(
                self, "No Project",
                "Please open or create a project first."
            )
            return

        if not os.path.isdir(proj_dir):
            QtWidgets.QMessageBox.critical(
                self, "Error",
                f"Project directory not found:\n{proj_dir}"
            )
            return

        file_path = self.file_path_edit.text()
        if not file_path or not os.path.isfile(file_path):
            QtWidgets.QMessageBox.warning(
                self, "No File",
                "Please select an input file first."
            )
            return

        self._update_project_info()
        self.console.clear()
        self.progress_bar.setValue(0)
        self.stage_label.setText("Preparing...")
        for btn in self.output_buttons.values():
            btn.setEnabled(False)
        self.open_gui_btn.setEnabled(False)
        self.open_klayout_btn.setEnabled(False)

        platform = self.platform_combo.currentText()

        if file_path.endswith(".cir.out"):
            cir_file = file_path
            design_name = os.path.basename(cir_file).replace(".cir.out", "")
            verilog_file = os.path.join(proj_dir, design_name + ".v")
        else:
            cir_file = None
            design_name = os.path.basename(file_path).replace(".v", "")
            verilog_file = file_path

        self._set_ui_busy(True)

        self.thread = QtCore.QThread(self)
        self.worker = OpenROADWorker(
            design_name, verilog_file, platform, cir_file
        )
        self.worker.moveToThread(self.thread)

        self.worker.progressChanged.connect(self.progress_bar.setValue)
        self.worker.statusChanged.connect(self.stage_label.setText)
        self.worker.logMessage.connect(self._append_log)
        self.worker.flowCompleted.connect(self._on_flow_completed)
        self.worker.flowFailed.connect(self._on_flow_failed)

        def cleanup():
            if self.thread is not None:
                self.thread.quit()
                self.thread.wait()
                self.thread = None
            self.worker = None
            self._set_ui_busy(False)

        self.worker.flowCompleted.connect(cleanup)
        self.worker.flowFailed.connect(cleanup)

        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def _cancel_flow(self):
        if self.worker is not None:
            self.worker.cancel()
        self.stage_label.setText("Cancelling...")
        self._append_log(
            f"[{datetime.now().strftime('%H:%M:%S')}] WARNING: Flow cancelled by user"
        )
        self.cancel_btn.setEnabled(False)

    def _on_flow_completed(self, outputs):
        self._outputs = outputs
        self.stage_label.setText("Completed")
        self.progress_bar.setValue(100)
        for btn in self.output_buttons.values():
            btn.setEnabled(True)

        gds_path = outputs.get("gds", "")
        if os.path.isfile(gds_path):
            self.open_gui_btn.setEnabled(True)
            self.open_klayout_btn.setEnabled(True)

    def _on_flow_failed(self, error):
        self._set_ui_busy(False)
        is_cancel = "cancelled" in error.lower()
        self.stage_label.setText("Cancelled" if is_cancel else "Failed")
        self.cancel_btn.setEnabled(False)
        if not is_cancel:
            QtWidgets.QMessageBox.critical(
                self, "Flow Failed",
                f"OpenROAD flow failed:\n\n{error}"
            )

    def _open_output(self, key):
        if self._outputs is None:
            return
        if key == "project":
            path = self._outputs.get("project_dir", "")
        else:
            path = self._outputs.get(key, "")
        if not path:
            return
        if os.path.isdir(path):
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path)
            )
        elif os.path.isfile(path):
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path)
            )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Not Found",
                f"File not found:\n{path}"
            )

    def _open_gui(self):
        proj = self.obj_appconfig.current_project
        proj_dir = proj.get("ProjectName", "")
        if not proj_dir:
            return
        try:
            subprocess.Popen(["openroad", "-gui"], cwd=proj_dir)
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                self, "Not Found",
                "OpenROAD GUI not found. Is OpenROAD installed?"
            )

    def _open_klayout(self):
        gds_path = self._outputs.get("gds", "") if self._outputs else ""
        if not gds_path or not os.path.isfile(gds_path):
            QtWidgets.QMessageBox.warning(
                self, "Not Found",
                "GDS file not found."
            )
            return
        try:
            subprocess.Popen(["klayout", gds_path])
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                self, "Not Found",
                "KLayout not found. Is KLayout installed?"
            )

