# AI CSV/Excel Assistant

This is a **Streamlit** application that uses **AI** to help you analyze and visualize your data from **CSV and Excel files**.


## How to Use

1. **Upload Files**: Drag and drop your `.csv`, `.xls`, or `.xlsx` files into the uploader.

2. **Select Data**: Choose the file and worksheet you want to work with from the dropdown menus.

3. **Ask Questions**: Type a question about your data in the text box.  
   _Examples:_  
   - “Show me the average sales per region”  
   - “Plot a bar chart of the top 5 products”

4. **Get Answers**: Click **Analyze**, and the AI will respond with:
   - A text-based explanation  
   - A table  
   - Or an auto-generated chart


## Features

- **Multi-file Upload**: Supports multiple CSV and Excel files
- **Natural Language Queries**: Ask questions in plain English
- **Automated Charts**: AI generates visualizations on the fly
- **Chat History**: Keeps a record of past queries and answers


## Setup

### Dependencies

Make sure you have **Python 3.x** and the following libraries installed:

```bash
pip install streamlit pandas openai python-dotenv pandasai
```

### API Key

You’ll need an **OpenAI API key**.

1. Create a `.env` file in your project directory.
2. Add the following line:

```env
MY_OPENAI_KEY="your_api_key_here"
```

> Do **not** share your `.env` file or commit it to GitHub.

### Run the App

In your terminal, navigate to the project folder and run:

```bash
streamlit run main.py
```

---

