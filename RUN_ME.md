# Running the extraction (Windows, ~15 minutes)

1. **Python**: install Python 3.11+ from python.org (tick "Add python.exe to PATH").
2. **Unzip** this folder somewhere simple, e.g. `C:\promise-card`.
3. **Gemini key**: go to aistudio.google.com → "Get API key" → Create API key. Copy it.
   Never paste the key into chat, the sheet or any file that goes to GitHub.
4. Open **Command Prompt** in the folder (type `cmd` in the File Explorer address bar, press Enter) and run:

```
pip install -r requirements.txt
set GEMINI_API_KEY=paste-your-key-here
python -m promise_card build --all --backend gemini --model gemini-3.5-flash-lite,gemini-3-flash-preview,gemini-3.8-flash
```

It prints one line per offer (about 25 lines, a few minutes). If an offer says FAILED, run the
same command with `--offer P13` (its ID) afterwards.

If it says the model name is not found, add `--model gemini-flash-latest` to the command.

5. Then run:

```
python -m promise_card eval --labels data/labels.csv > results.json
```

6. Zip the `data\extractions` and `data\cards` folders plus `results.json` and send them back.

The folder contains private material (provider documents, your friends' letters). Do not push
`evidence/`, `data/sources/`, `data/labels.csv` or `data/offers.csv` to GitHub; `.gitignore` already
excludes them.
