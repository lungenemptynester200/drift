# 🧭 drift - Find code drift before it spreads

[![Download drift](https://img.shields.io/badge/Download-drift-blue?style=for-the-badge)](https://github.com/lungenemptynester200/drift)

## 🌟 What drift does

drift checks code for signs that the design is starting to break down. It looks for:

- repeated patterns that no longer match
- places where the code does not follow the intended structure
- near-duplicate code that can cause bugs later
- changes from AI-generated code that add noise or split patterns

If you use AI tools, drift helps you spot when the code starts to wander from the shape you want.

## 💻 What you need

Before you run drift on Windows, make sure you have:

- Windows 10 or later
- Python 3.10 or newer
- Git, if you want to copy the project from GitHub
- A command window, such as PowerShell or Windows Terminal

If you plan to scan a project, keep the source code folder on your computer as well.

## 📥 Download drift

Visit this page to download or get the project files:

[drift on GitHub](https://github.com/lungenemptynester200/drift)

If the page includes a release, download the Windows file from there. If it gives you the source files, copy them to your computer first and then run the tool from the project folder.

## 🪟 Install on Windows

### Option 1: Use a release file

If the GitHub page gives you a Windows file, do this:

1. Download the file to your computer.
2. Open the Downloads folder.
3. Double-click the file to start it.
4. If Windows shows a security prompt, choose the option to run it.
5. Follow the on-screen steps.

### Option 2: Run from the project folder

If the GitHub page gives you the source files, do this:

1. Download the project as a ZIP file.
2. Right-click the ZIP file and choose Extract All.
3. Open the extracted folder.
4. Open PowerShell in that folder.
5. Run the command shown in the project files to start drift.

## 🛠️ First-time setup

If you are starting from the source files, set up Python first.

1. Install Python from the official Python website if it is not on your PC.
2. Open PowerShell.
3. Check that Python works by typing:

   `python --version`

4. If the project uses a virtual environment, create it with the command in the project folder.
5. Install the required packages with the command listed in the project files.

A common setup flow looks like this:

1. Open the drift folder.
2. Open PowerShell in that folder.
3. Install the needed packages.
4. Run the drift command against your code folder.

## ▶️ How to run drift

After setup, you can run drift from the project folder.

Typical use looks like this:

1. Open PowerShell.
2. Move to the folder where drift is saved.
3. Run drift with the folder you want to check.

Example:

`python -m drift <your-code-folder>`

You can replace `<your-code-folder>` with the path to the project you want to scan.

## 🔍 What drift looks for

drift checks code in a few useful ways.

### Pattern fragmentation

This finds places where a repeated design starts to split into many small versions. That can make the code harder to follow.

### Architecture violations

This finds code that does not fit the intended structure. For example, a low-level module may start calling a high-level one in a way that should not happen.

### Mutant duplicates

This finds code blocks that look almost the same but are not exact copies. These are hard to track and often point to cleanup work.

### AI code drift

This helps when code comes from AI tools. AI code can work well at first, but it can also add extra shapes, mixed styles, or repeated logic. drift helps catch that early.

## 🧭 How to read the results

When drift finishes a scan, it gives you a report. Look for:

- file names
- line numbers
- repeated patterns
- structure breaks
- duplicate blocks

Start with the items that appear in many files. Those often point to a bigger design issue.

If you see the same kind of warning in several places, fix the shared pattern first. That usually saves time.

## 🧹 Good ways to use drift

Use drift when you:

- add AI-generated code to a project
- review a pull request
- clean up old code
- split a large feature into smaller parts
- want to keep a codebase easy to maintain

A simple routine works well:

1. Run drift before you merge changes.
2. Review the report.
3. Fix the largest structure problems first.
4. Run it again after the changes.

## 📁 Example workflow

A simple Windows workflow looks like this:

1. Download the project from GitHub.
2. Open the folder in File Explorer.
3. Open PowerShell in that folder.
4. Install Python packages if needed.
5. Run drift on the folder you want to check.
6. Read the report and clean up the code.

This keeps the codebase easier to maintain and easier to review.

## ⚙️ Common commands

These examples follow a plain Python workflow:

- Check Python:

  `python --version`

- Run drift on a folder:

  `python -m drift C:\path\to\your\project`

- Save the report to a file if the tool supports it:

  `python -m drift C:\path\to\your\project > report.txt`

If the project includes a different command in its files, use that one.

## 🧩 Who this is for

drift is useful for:

- people who use AI coding tools
- developers who want cleaner structure
- code reviewers
- teams that want less technical debt
- anyone who wants to spot code drift early

You do not need deep coding knowledge to start using it. If you can open a folder and run a command, you can use drift.

## 🗂️ Project topics

This project fits work around:

- AI-generated code
- architecture checks
- CLI tools
- code quality
- code review
- GitHub Actions
- linting
- static analysis
- technical debt

## 🛟 If something does not work

If drift does not start, check these steps:

1. Make sure Python is installed.
2. Make sure you are in the correct folder.
3. Make sure the folder you scan exists.
4. Check that any required packages are installed.
5. Run the command again and read the error text.

If Windows blocks the file, try extracting it again or running it from a local folder like Documents or Desktop.

## 📄 Where to get the files

Get the project here:

[https://github.com/lungenemptynester200/drift](https://github.com/lungenemptynester200/drift)

## 🔐 Working with your code

When you run drift on your own project, it only needs access to the files you point it at. A good habit is to scan a copy of the code first if you want to test the tool without touching your main work folder

## 🧪 What to check after the first scan

After your first run, look at:

- the most repeated warnings
- files that show up many times
- places where structure is unclear
- duplicate logic that should be shared
- code added by AI that does not match the rest of the project

Then fix one issue at a time and scan again to see what changed