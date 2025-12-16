# Company BOT
## Requirements
- `Python 3.12.10`
## Installation
- Download the repository as a zip and extract OR use `git clone https://github.com/BleedFeed/company-bot.git`
- Open a terminal session (cmd, sh, bash) and navigate to `company-bot-main` folder
- Create a Python virtual env inside `company-bot-main` using the command `python -m venv venv`
- Activate the virtual environment you just created by entering the command `.\venv\Scripts\activate`
- Install dependencies using `pip install -r requirements.txt`
- Update the resource ID at the top of the `bot.py` file `RESOURCE_ID = 60`, where 60 corresponds to the underwear resource.
- Create an `.env` file and add these keys E-MAIL, PASSWORD, PYTHON_PATH
  - Example of a `.env` file:
  ```
  E-MAIL="email@gmail.com"
  PASSWORD="your_password_here"
  PYTHON_PATH=.\venv\Scripts\python ## No need to change if you did virtual env steps.
  ```

### Usage
- Activate the venv (virtual env) you created by `.\venv\Scripts\activate`
- Then run the script with the number of hours as an argument:
  - `python bot.py <hours>`
  - Example: `python bot.py 24` retails for 24 hours.
  - Another Example: `python bot.py 23+59/60` sells for 23 hours 59 minutes
  
## Optional
- You can use the Windows task scheduler and run `bot.vbs` file to fully automate.
- Use the action below and a trigger of your choice
  - Action: Start a program
  - Program / script: `wscript.exe`
  - Add arguments: `"PATH TO YOUR BOT.VBS" <hours>` EXAMPLE: `"C:\Users\EREN\zartzurt\company-bot-main\bot.vbs" 23+59/60`
  - Start in: `PATH TO YOUR BOT.VBS PARENT FOLDER` EXAMPLE: `C:\Users\EREN\zartzurt\company-bot-main`
