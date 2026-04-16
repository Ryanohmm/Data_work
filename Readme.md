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

- Once everything is installed and running, enter data.ipynb and click run all to look through the cleaning process and graphs. You can then go to comics.py and run that which should creat comics.db. Then you can navigate to comics.db and browse the DB.

- Explore the project files:
    - **`data.ipynb`**  
        - Contains data cleaning steps  
        - Imports  
        - Graphs and visualizations  
    - **`comics.py`**  
        - Builds the SQLite database  
        - Contains helper functions  
    - **`cleaned_characters.csv`**  
        - CSV version of the database schema  
    - **`Comic Database Schema.png`**  
        - Visual flowchart of the project structure  
    - **`dc-wikia-data.csv`** and **`marvel-wikia-data.csv`**  
        - Raw datasets used for cleaning and graph generation  
    - **comics.db**  
        - Contains data from both datasets. 
        

---



# 🔗 Links (Credit Sources)

- **Dataset Sources:**  
  - Kaggle Source: [https://www.kaggle.com/datasets/fivethirtyeight/fivethirtyeight-comic-characters-dataset/data?select=marvel-wikia-data.csv] (https://www.kaggle.com/datasets/fivethirtyeight/fivethirtyeight-comic-characters-dataset/data?select=marvel-wikia-data.csv)
  - Marvel Wikia Data: (marvel-wikia-data.csv)  
  - DC Wikia Data:(dc-wikia-data.csv)

---

---


# 📊 Project Summary

- This project combines Marvel and DC character data from the FiveThirtyEight Comic Characters dataset and transforms it into a structured SQLite database for analysis. The workflow moves from raw CSV files to a fully populated relational database.

- The Jupyter notebook (data.ipynb) handles the data‑cleaning process. It merges the two datasets, removes incomplete or invalid records, standardizes key fields, and filters the characters down to meaningful entries. The cleaned results are exported as cleaned_characters.csv, containing each character’s name, alignment, gender, publisher, appearance count, and first appearance year.

- The comics.py script builds a simplified, normalized database using four tables: Characters, Sex, Align, and Appearances. It loads the cleaned CSV, creates the schema, populates each table, and includes helper functions for searching and exploring character data.

- Together, the notebook and script form a complete ETL pipeline that supports analysis of character, gender and alignment trends. The project demonstrates practical skills in data cleaning, transformation, database design, and Python automation.

---

