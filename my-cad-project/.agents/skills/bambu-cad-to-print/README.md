# Bambu CAD-to-Print Agent Skill

Portable `SKILL.md` skill for converting native CAD, STEP, surfaces, 3D render meshes or 2D-render references into **verifiable** Bambu Lab FDM prints. Includes design rules, dimension/source notes, checklists, a reusable job brief, report template and an STL mesh QA script.

## Quick install (agent that supports Agent Skills)
1. Copy the complete `bambu-cad-to-print` folder (not only `SKILL.md`) into your agent's recognized skill directory.
2. In OpenAI Codex, for a repository, use `.agents/skills/bambu-cad-to-print/SKILL.md` (and companion files). In a Claude Code repository, use `.claude/skills/bambu-cad-to-print/SKILL.md`. Skill discovery varies across products; check current host documentation.
3. For ChatGPT desktop / Work, use the supported skills/skill-creator interface or package as a plugin if distributing broadly. Standard ChatGPT chat attachments by themselves are not persistent installation of skills. You can also attach `SKILL.md` to a single chat as reference instructions, with limitations.
4. In a custom agent that accepts a system/developer instruction but not skill folders, supply the contents of `SKILL.md` as the agent's standing instruction and make the `references/` and `assets/` files accessible. Scripts run only if the agent has an execution tool.
5. Version-control the folder with the CAD repo and maintain printer/nozzle/material presets separately for reproducibility.

## Example prompt to activate
> Use the `bambu-cad-to-print` skill. Create a printable [part] from [native CAD/STEP/OBJ/rendered image]. Target [Bambu model], [nozzle] and [filament]. My critical dimensions are [...] in mm. Preserve editable CAD, export a dimensionally verified STL, run mesh QA, and review the Bambu Studio slice if tools permit. Give me files and the gate-by-gate QA report. Never claim a test that wasn't performed.

## Automated check
Install requirements on an environment where you trust the dependencies:

```sh
python -m pip install -r requirements.txt
python scripts/validate_stl.py model.stl --units mm --build-volume 256 256 256 --json mesh-qa.json
```

The `256 256 256` is an **example only**; replace it with the exact usable build volume and check machine exclusions in the slicer. The script does not repair meshes and cannot prove wall thickness, supportability, self-intersection freedom or physical fit. It returns exit code 0 on checked geometry pass, 1 on mesh validation fail, 2 on usage/dependency error.

## Robust deployment advice
- Keep the `SKILL.md` focused on reproducible gates. Put rules and templates in supporting files so the agent loads them only when necessary.
- Give the agent CAD/mesh-editing tools (e.g., FreeCAD scripting, Fusion API or Blender) **and** the slicer. Written instructions without these tools cannot generate or slice a part.
- For a repeatable team workflow, expose CAD/mesh operations and Bambu Studio checks through controlled tools or an MCP integration (when available). Require human approval for printer dispatch.
- Build a small physical calibration library for each nozzle/material/printer combination: hole gauge, gap coupon, bridge/overhang test and strength coupon if relevant. Record resulting offsets in a machine-specific file, not as globally true numbers.

## Authoritative reading
- Bambu Studio: https://wiki.bambulab.com/en/software/bambu-studio/studio-quick-start
- Bambu Studio wall generator: https://wiki.bambulab.com/en/software/bambu-studio/wall-generator
- Bambu STEP import: https://wiki.bambulab.com/en/software/bambu-studio/step
- Prusa design for 3D printing: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- OpenAI skill format / distribution: https://learn.chatgpt.com/docs/build-skills
- Agent Skills: https://agentskills.io/specification

Version 1.0.0. Values are documented starting points, not certified print specifications.
