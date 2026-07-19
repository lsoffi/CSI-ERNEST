# ERNEST CSI

ERNEST CSI is a small Python generator for classroom science investigation dossiers.

CSI stands for **Classroom Science Investigation**. The format turns a physics activity into an investigative case file: students read a scenario, examine evidence, choose hypotheses, design simple measurements, collect data, build graphs, and use the results to support a scientific conclusion.

The current case, `CSI-001 - L'orologio del museo`, focuses on the motion of a pendulum. The story is designed so students can naturally investigate how the pendulum period may change when they vary physical conditions such as the bob mass, the release angle, or the string length. The student dossier does not prescribe those tests directly; instead, the scene, materials, and mission make those comparisons possible. The teacher guide explains the expected physics more explicitly, including the importance of using small initial angles.

## What The Generator Produces

For each case in the data file, the generator creates two A5 portrait PDFs:

- a student case file
- a teacher guide

The current `output/` folder is intentionally kept clean and contains only the latest two generated PDFs:

```text
output/
├── csi-001-l-orologio-del-museo-student.pdf
└── csi-001-l-orologio-del-museo-teacher-guide.pdf
```

Both PDFs include the same ERNEST-style cover. The teacher guide then adds the complete teaching notes, including phenomenon explanation, measurement guidance, expected results, interpretation, safety notes, and debrief prompts.

## Student Case File Structure

The student dossier is designed for classroom use by students aged roughly 11-14. It contains:

- an investigative cover with the case scenario
- a schematic drawing area for students to represent the physics case
- evidence and witness statements
- a mission box
- a notebook page for key clues, observations, hypotheses, and free notes
- three open experiment sheets
- an evidence analysis page
- a final scientific report page

The experiment sheets are deliberately open. Students choose what to compare, define `x` and `y`, record data, draw a graph, and interpret what the experiment shows.

## Teacher Guide Structure

The teacher guide includes:

- the same cover as the student dossier
- case overview
- learning objectives
- explanation of the physics phenomenon
- measurement guidance
- expected results and interpretation
- materials list
- setup instructions
- 30-minute classroom timeline
- expected solution
- debrief questions
- real-world connection
- safety notes

For the pendulum case, the teacher guide clarifies that the simple pendulum model works best for small initial angles, approximately 5-15 degrees. It also explains that, under classroom conditions, the period depends mainly on string length, while changing bob mass or small initial angle should have little effect if the other conditions are controlled.

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── assets/
│   ├── ERNEST-logo.svg
│   ├── ERNEST-logo.svg.png
│   ├── ERNEST-logo-transparent.png
│   ├── ERNEST-watermark.png
│   └── eu-funded-logo.png
├── data/
│   ├── cases.csv
│   └── cases.json
├── output/
│   ├── csi-001-l-orologio-del-museo-student.pdf
│   └── csi-001-l-orologio-del-museo-teacher-guide.pdf
├── src/
│   ├── generate.py
│   ├── pdf_builder.py
│   └── templates.py
└── templates/
    ├── student_case.yml
    └── teacher_guide.yml
```

## Installation

Create a virtual environment and install the Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies:

- `reportlab` for PDF layout and generation
- `pypdf` for optional PDF merging
- `PyYAML` for template-related support
- `svglib` for SVG logo rendering fallback

## Generating PDFs

Generate from JSON:

```bash
python src/generate.py --input data/cases.json
```

Generate from CSV:

```bash
python src/generate.py --input data/cases.csv
```

Generate into a custom output folder:

```bash
python src/generate.py --input data/cases.json --output output
```

Optional combined PDFs can still be generated with:

```bash
python src/generate.py --input data/cases.json --combined
```

However, the current working convention for this project is to keep `output/` clean and store only the two current case PDFs.

## Data Files

Cases can be edited in either `data/cases.json` or `data/cases.csv`.

The generator accepts both formats. JSON is easier to read and edit for longer text; CSV is useful for spreadsheet-based workflows.

The column and field names are in English for technical stability, but the content can be written in any target language. The current case content is in Italian.

## Case Data Fields

| Field | Purpose |
| --- | --- |
| `case_id` | Case code, for example `CSI-001`. |
| `title` | Case title. |
| `age_group` | Target age group. This is kept in the data even if it is not displayed on the current cover. |
| `physics_topic` | Main physics topic and investigation focus. |
| `cover_image` | Legacy optional field. The current design uses a schematic drawing box instead of a case image. |
| `mystery` | Main scenario problem. |
| `story_intro` | Narrative introduction and context. |
| `scene_evidence` | Evidence found in the scene. |
| `witness_1` | First witness statement or clue voice. |
| `witness_2` | Second witness statement or clue voice. |
| `witness_3` | Third witness statement or clue voice. |
| `mission` | What students are asked to investigate. |
| `hypothesis_1` | Teacher reference hypothesis. The student file leaves hypothesis space blank. |
| `hypothesis_2` | Teacher reference hypothesis. |
| `hypothesis_3` | Teacher reference hypothesis. |
| `variable_changed` | Teacher-facing guidance on possible independent variables. |
| `quantity_measured` | Teacher-facing guidance on the measured quantity. |
| `expected_graph` | Teacher-facing expected graph or graph family. |
| `graph_shape` | Expected trend or graph shape. |
| `materials` | Materials needed for the classroom activity. |
| `teacher_solution` | Expected explanation or solution. |
| `educational_message` | Final scientific takeaway for students. |
| `real_world_connection` | Link to research, technology, daily life, or real instruments. |
| `step_1_observe` | Timeline prompt for observation. |
| `step_2_hypothesize` | Timeline prompt for hypothesis building. |
| `step_3_experiment` | Timeline prompt for experimentation. |
| `step_4_record_data` | Timeline prompt for recording data. |
| `step_5_build_graph` | Timeline prompt for graph building. |
| `step_6_conclusion` | Timeline prompt for conclusion. |

## Current Pendulum Case Notes

The pendulum case is written so that students can discover which variable is most relevant to the clock delay.

The evidence includes:

- different metal weights
- an adjustable string with marks or knots
- references for small release angles
- scene clues that may or may not be important

The student mission asks students to choose what to compare, change only one condition at a time, use small initial angles, and measure the period from the time for 10 oscillations.

The teacher guide explains the expected interpretation:

- changing string length changes the period clearly
- changing bob mass should not significantly change the period if length and angle are controlled
- changing small initial angles should not significantly change the period
- large angles should be avoided when comparing with the simple pendulum model

## Design Notes

- Page size: A5 portrait.
- Each page has an external ERNEST-style frame.
- All content boxes are designed to stay inside the frame.
- The EU funding footer sits below the frame on every page.
- The cover uses an ERNEST watermark and a scenario box.
- The student file uses a drawing-grid box instead of a case image.
- The teacher guide shares the same cover as the student file.

## Regenerating A Clean Output Folder

To keep only the two latest PDFs in `output/`, remove old PDFs and regenerate without `--combined`:

```bash
rm output/*.pdf
python src/generate.py --input data/cases.json
```

Be careful when deleting files. The command above removes every PDF currently in `output/`.
