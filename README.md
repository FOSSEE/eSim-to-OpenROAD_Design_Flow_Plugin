# eSim OpenROAD Design Flow Plugin

The eSim OpenROAD Design Flow Plugin connects the eSim schematic capture and simulation workflow with the OpenROAD physical design flow. It helps users move from circuit design and simulation toward RTL-to-GDSII generation using open-source EDA tools.

This project is intended for the FOSSEE eSim ecosystem and Ubuntu-based setup workflows.

## Features

- Integrates eSim with the OpenROAD Flow Scripts.
- Provides setup scripts for installing eSim and required dependencies.
- Includes example circuits and reference design data.
- Supports OpenROAD GUI usage for viewing generated layouts.
- Includes helper scripts for OpenROAD flow setup and plugin integration.

## Repository Structure

| Path | Description |
| --- | --- |
| `src/` | Python source code for eSim modules and OpenROAD integration. |
| `Examples/` | Sample eSim circuits and design examples. |
| `library/` | Device models, subcircuits, manuals, and bundled reference files. |
| `install-eSim-scripts/` | Supporting installation scripts. |
| `install-eSim.sh` | Main install and uninstall script. |
| `orfs-setup.py` | OpenROAD Flow Scripts setup helper. |
| `install.md` | Detailed installation and usage guide. |
| `contribution.md` | Contribution guidelines. |
| `docker-launcher/` | Docker environment and launcher scripts for running the eSim OpenROAD integration workflow. |


## Documentation

For the full setup workflow, see [`install.md`](install.md).

For the docker setup workflow, see [`docker.md`](docker-launcher/README.md)

For contribution guidelines, see [`contribution.md`](contribution.md).

## License

This project is licensed under the terms included in [`LICENSE`](LICENSE).
