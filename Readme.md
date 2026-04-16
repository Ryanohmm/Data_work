# 📘 Project Setup & Overview

To run this project successfully, complete the following steps:

- Install all required Python packages  
    ```bash
    pip install -r requirements.txt
    ```

- Create a virtual environment  
    ```bash
    python -m venv .venv
    ```
    - *(You can rename `.venv` to anything you like — `.comiccity` works too.)*

- Install a SQLite viewer extension in VS Code  
    - **SQLite Viewer**  
    - **SQLite Explorer Plus**  
    - *(Either one will let you inspect the database.)*

- Explore the project files:
    - **`data.ipynb`**  
        - Contains data cleaning steps  
        - Imports  
        - Graphs and visualizations  
    - **`comics.py`**  
        - Builds the SQLite database  
        - Contains helper functions  
    - **`Comic_Database_Schema.csv`**  
        - CSV version of the database schema  
    - **`flowchart.png`**  
        - Visual flowchart of the project structure  
    - **`dc-wikia-data.csv`** and **`marvel-wikia-data.csv`**  
        - Raw datasets used for cleaning and graph generation  
    - **Database file**  
        - Contains fictional sample data aligned with the comic book dataset  
        - *(Not pulled directly from the original datasets)*

---

# 🔗 Links (Replace with your own)

- **Project Repository:**  
  [Insert GitHub Repo Link Here](https://example.com)

- **Dataset Sources:**  
  - Marvel Wikia Data: [Insert Link](https://example.com)  
  - DC Wikia Data: [Insert Link](https://example.com)

---

# 🖼️ Images (Replace with your own)

![Flowchart Placeholder](https://example.com/flowchart.png)  
*Project flowchart*

![Graph Placeholder](https://example.com/graph.png)  
*Example graph or chart*
