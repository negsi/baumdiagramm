# Baumdiagramm

This project provides a lightweight, modular framework for working with general tree structures. It supports creating, storing, traversing, and analyzing trees using clean abstractions and a flexible persistence layer. The toolkit includes utilities for importing and exporting trees, generating random structures, computing statistics, and validating consistency, making it ideal for experiments, data modeling, and architectural prototyping.

---

## 🚀 Requirements

- Python 3.10 or newer  
- pip (Python Package Installer)  
- Optional: a virtual environment (recommended)

---

## 📦 Installation

### 1. Clone or download repository

```bash
git clone https://github.com/negsi/baumdiagramm.git
cd baumdiagramm
```

### 2. Create a virtual environment (optional, but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage
All commands are accessed through the main `cli.py` script.
```bash
python cli.py [COMMAND] [ARGS]
```

---

### 1. Node Management

#### `tree-add-node`
Creates a new node.
*   **Args:** `value` (string), `parent_id` (optional).
*   **Example:**
    ```bash
    python cli.py tree-add-node "My Root"
    python cli.py tree-add-node "Child Node" 1
    ```

#### `tree-move-node`
Moves a node (and its entire subtree) to a new parent.
*   **Args:** `node_id`, `new_parent_id` (optional).
*   **Example:**
    ```bash
    # Move node 5 under node 2
    python cli.py tree-move-node 5 2
    # Move node 5 to become a root
    python cli.py tree-move-node 5
    ```

#### `tree-delete-node`
Removes a node from the tree. *Note: Descendants are not automatically deleted or re-parented.*
*   **Args:** `node_id`.
*   **Example:**
    ```bash
    python cli.py tree-delete-node 5
    ```

---

### 2. Listing & Querying

#### `tree-list-roots`
Lists all top-level nodes (nodes with no parent).
*   **Example:**
    ```bash
    python cli.py tree-list-roots
    ```

#### `tree-list-subtree` | `tree-list-ancestors` | `tree-list-descendants`
Retrieve specific subsets of the tree.
*   **Args:** `node_id`.
*   **Example:**
    ```bash
    python cli.py tree-list-subtree 1
    python cli.py tree-list-ancestors 5
    ```

#### `tree-find`
Search for nodes by value (case-insensitive).
*   **Args:** `query`.
*   **Example:**
    ```bash
    python cli.py tree-find "Search Term"
    ```

#### `tree-info`
Display metadata for a specific node.
*   **Args:** `node_id`.

---

### 3. Visualization & Export

#### `tree-print`
Prints a visual ASCII representation of the tree in the terminal.
*   **Args:** `root_id`.

#### `tree-export-json` / `tree-import-json`
Export/Import the tree structure as JSON.
*   **Export:** `python cli.py tree-export-json 1 > tree.json`
*   **Import:** `python cli.py tree-import-json data.json --parent 1`

#### `tree-export-dot`
Export the tree in Graphviz DOT format for visualization tools.
*   **Args:** `root_id`.

---

### 4. Analysis & Generation

#### `tree-stats`
Display structural statistics (count, depth, leaf nodes, branching factor).
*   **Args:** `root_id`.

#### `tree-validate`
Checks the integrity of the database closure table (detects cycles, zombie paths, or missing links).
*   **Usage:** `python cli.py tree-validate`

#### Random Data Generation
Useful for testing and performance benchmarking.

*   **`tree-generate-random`**: Generates a tree and imports it into the DB.
*   **`tree-generate-random-json`**: Prints random tree JSON to stdout (use for files).
*   **`tree-generate-huge`**: Generates a larger tree for stress testing.

*   **Common Options:**
    *   `--max-depth`: Max hierarchy level.
    *   `--max-children`: Max children per node.
    *   `--prefix`: String prefix for node values.

*   **Example:**
    ```bash
    python cli.py tree-generate-random --max-depth 3 --max-children 5
    ```