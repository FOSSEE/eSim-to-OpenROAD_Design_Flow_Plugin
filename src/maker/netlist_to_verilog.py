import os
import re
import sys
import shutil
import subprocess


# ─────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────

def fail(message, code=1):
    print(f"[✗] {message}", file=sys.stderr)
    sys.exit(code)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def normalize_module_name(name):
    """
    Preserves original case (Halfwave_Rectifier stays Halfwave_Rectifier).
    Only fixes invalid characters and collapses double underscores.
    """
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')


# ─────────────────────────────────────────────────────────────
# ALL ORFS STAGE ODB FILES IN ORDER
# Script will check from last to first and open
# the GUI at whichever stage completed successfully.
# ─────────────────────────────────────────────────────────────

STAGE_ODBS = [
    ("6_final.odb",        "Stage 6 - Final"),
    ("5_route.odb",        "Stage 5 - Routing"),
    ("4_cts.odb",          "Stage 4 - Clock Tree Synthesis"),
    ("3_5_place_dp.odb",   "Stage 3.5 - Detail Placement"),
    ("3_4_place_resized.odb", "Stage 3.4 - Resizing"),
    ("3_3_place_mpl.odb",  "Stage 3.3 - Macro Placement"),
    ("3_2_place_iop.odb",  "Stage 3.2 - IO Placement"),
    ("3_1_place_gp.odb",   "Stage 3.1 - Global Placement"),
    ("2_floorplan.odb",    "Stage 2 - Floorplan"),
    ("1_synth.odb",        "Stage 1 - Synthesis"),
]


def find_latest_odb(orfs_flow, module_name):
    """
    Checks all stage ODB files from last to first.
    Returns (odb_filename, stage_label) of the furthest completed stage.
    """
    base_dir = os.path.join(orfs_flow, "results", "sky130hd", module_name, "base")

    print(f"\n[*] Checking completed stages in: {base_dir}")

    for odb_file, stage_label in STAGE_ODBS:
        full_path = os.path.join(base_dir, odb_file)
        if os.path.isfile(full_path):
            print(f"[✓] Found: {stage_label} → {odb_file}")
            return odb_file, stage_label

    return None, None


# ─────────────────────────────────────────────────────────────
# VERILOG SEARCH
# ─────────────────────────────────────────────────────────────

def find_generated_verilog(selected_path, project_name, orfs_design_dir):
    project_dir = os.path.dirname(selected_path) or "."
    home_dir    = os.path.expanduser("~")

    candidates = [
        os.path.join(project_dir, f"{project_name}.v"),
        os.path.join(home_dir, f"{project_name}.v"),
        os.path.join(orfs_design_dir, f"{project_name}.v"),
        selected_path.replace(".cir.out", ".v"),
    ]

    print("[*] Looking for Verilog file in:")
    for path in candidates:
        print(f"    - {path}")
        if os.path.isfile(path):
            print(f"[✓] Found Verilog: {path}")
            return path

    return None


# ─────────────────────────────────────────────────────────────
# VERILOG INSPECTION
# ─────────────────────────────────────────────────────────────

def extract_top_module_name(verilog_path):
    with open(verilog_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_]*)", content, re.MULTILINE)
    if not match:
        fail(f"Could not find module name in: {verilog_path}")
    return match.group(1)


def is_clocked_design(verilog_path):
    with open(verilog_path, "r", encoding="utf-8") as f:
        content = f.read()
    return (
        re.search(r"\bposedge\b",               content)               is not None or
        re.search(r"\bnegedge\b",               content)               is not None or
        re.search(r"\binput\s+.*\bclk\b",       content, re.IGNORECASE) is not None or
        re.search(r"\binput\b[^;\n]*\bclock\b", content, re.IGNORECASE) is not None
    )


# ─────────────────────────────────────────────────────────────
# FILE BUILDERS
# ─────────────────────────────────────────────────────────────

def build_config(module_name, project_name):
    return f"""export DESIGN_NAME = {module_name}
export PLATFORM    = sky130hd
export VERILOG_FILES = ./designs/sky130hd/{project_name}/{project_name}.v
export SDC_FILE      = ./designs/sky130hd/{project_name}/constraint.sdc
export DIE_AREA  = 0 0 100 100
export CORE_AREA = 10 10 90 90
"""


def build_sdc(is_clocked):
    if is_clocked:
        return "create_clock [get_ports clk] -period 10\n"
    return "set_units -time ns\n"


def build_gui_tcl(module_name, stage_odb):
    return (
        f"read_db ./results/sky130hd/{module_name}/base/{stage_odb}\n"
        "gui::fit\n"
    )


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        fail("Usage: python3 openroad_integration.py <path_to_project.cir.out>")

    selected_path = os.path.abspath(sys.argv[1])
    project_name  = os.path.basename(selected_path).replace(".cir.out", "")

    print(f"\n{'='*60}")
    print(f"  OpenROAD Integration — Project: {project_name}")
    print(f"{'='*60}\n")
    print(f"[*] Selected file: {selected_path}")

    # ── ORFS paths ───────────────────────────────────────────
    orfs_root    = os.path.expanduser("~/OpenROAD-flow-scripts")
    orfs_flow    = os.path.join(orfs_root, "flow")
    docker_shell = os.path.join(orfs_flow, "util", "docker_shell")

    if not os.path.isdir(orfs_flow):
        fail(f"OpenROAD flow directory not found: {orfs_flow}")
    if not os.path.isfile(docker_shell):
        fail(f"docker_shell not found: {docker_shell}")
    if shutil.which("docker") is None:
        fail("docker is not installed or not in PATH")

    # ── Design directory ─────────────────────────────────────
    design_dir = os.path.join(orfs_flow, "designs", "sky130hd", project_name)
    os.makedirs(design_dir, exist_ok=True)

    # ── Find Verilog ─────────────────────────────────────────
    verilog_path = find_generated_verilog(selected_path, project_name, design_dir)

    if verilog_path is None:
        fail(
            f"Verilog file '{project_name}.v' not found.\n"
            f"Please place your Verilog file in ONE of these locations:\n"
            f"  1. {os.path.dirname(selected_path)}/{project_name}.v\n"
            f"  2. ~/{project_name}.v\n"
            f"  3. {design_dir}/{project_name}.v"
        )

    # ── Extract module info ──────────────────────────────────
    module_name = extract_top_module_name(verilog_path)
    module_name = normalize_module_name(module_name)
    clocked     = is_clocked_design(verilog_path)

    print(f"[*] Module name : {module_name}")
    print(f"[*] Design type : {'clocked' if clocked else 'combinational'}")
    print(f"[*] Flow target : {'finish' if clocked else 'place'}")

    # ── Copy Verilog + write config files ────────────────────
    target_verilog = os.path.join(design_dir, f"{project_name}.v")
    target_sdc     = os.path.join(design_dir, "constraint.sdc")
    target_config  = os.path.join(design_dir, "config.mk")

    shutil.copyfile(verilog_path, target_verilog)
    print(f"[*] Copied Verilog  : {target_verilog}")

    write_file(target_sdc,    build_sdc(clocked))
    print(f"[*] Wrote SDC       : {target_sdc}")

    write_file(target_config, build_config(module_name, project_name))
    print(f"[*] Wrote config.mk : {target_config}")

    # ── Environment ──────────────────────────────────────────
    env = os.environ.copy()
    env["QT_X11_NO_MITSHM"]      = "1"
    env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    env["OPENROAD_EXE"] = "/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad"
    env["YOSYS_EXE"]    = "/usr/local/bin/yosys"

    # ── Run ORFS flow ─────────────────────────────────────────
    design_config = f"./designs/sky130hd/{project_name}/config.mk"
    flow_target   = "finish"

    cmd = [docker_shell, "make", f"DESIGN_CONFIG={design_config}", flow_target]

    print(f"\n[*] Running: make DESIGN_CONFIG={design_config} {flow_target}")
    print("-" * 60)

    result = subprocess.run(
        cmd,
        cwd=orfs_flow,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(result.stdout)

    if result.returncode != 0:
        print(f"[!] Flow exited with code {result.returncode} — checking how far it got...")
    else:
        print(f"[✓] Flow completed successfully!")

    # ── Find latest completed ODB ─────────────────────────────
    # Works whether flow succeeded OR failed halfway.
    # Opens GUI at whatever stage was last completed.
    stage_odb, stage_label = find_latest_odb(orfs_flow, module_name)

    if stage_odb is None:
        fail(
            f"No ODB files found at any stage.\n"
            f"Flow likely failed at synthesis. Check logs:\n"
            f"  ~/OpenROAD-flow-scripts/flow/logs/sky130hd/{module_name}/base/"
        )

    print(f"\n[*] Opening GUI at: {stage_label}")

    # ── Launch GUI ────────────────────────────────────────────
    gui_tcl_path = os.path.join(orfs_flow, f"open_gui_{module_name}.tcl")
    write_file(gui_tcl_path, build_gui_tcl(module_name, stage_odb))
    print(f"[*] Wrote GUI Tcl: {gui_tcl_path}")

    gui_cmd = [
        docker_shell,
        "openroad", "-gui",
        f"./{os.path.basename(gui_tcl_path)}",
    ]

    print(f"[*] Launching: openroad -gui ./{os.path.basename(gui_tcl_path)}")

    gui_result = subprocess.run(
        gui_cmd,
        cwd=orfs_flow,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(gui_result.stdout)

    if gui_result.returncode != 0:
        fail(f"OpenROAD GUI failed with exit code {gui_result.returncode}")

    print(f"\n[✓] OpenROAD GUI closed for '{project_name}'")


if __name__ == "__main__":
    main()
