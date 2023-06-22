# Snapshot Diff FTP

A little tool to push the differences of your folder which are happened between the two snapshots to the ftp destination.

## Configuration
Create a `.env` in the cloned repository and set the following variables.
```env
INTERVAL = 1
BASE_DIR = "./"
FTP_BASE_DIR = "/"
FTP_PORT = 21
FTP_HOST = "localhost"
FTP_USER = "user"
FTP_PASS = "pass"
FTP_PASSIV = true
```
 
## Usage
Just run the script.
```bash
python311 ./main.py
```
and enjoy coding! <3
