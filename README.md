# Installation
First prepare your environment. It is recommended to use venv, but this is optional.
1. Clone the repository
2. Create and activate your venv (if using a virtualenvironment) and run `pip install -r requirements.txt'

To use this script you first have to populate the database. This only has to be done once per platform.
1. From the Datomatic, download the DB file from the platforms you'd like to load. Ensure you are downloading the DB version of the file and not the dat or P/C.
2. Extract the files and copy them to the "xmls" directory.
3. Rename the files to the correct syntax. This is "ID Company - Platform.xml".
No-Intro database files are named like this by default: "Nintendo - Game Boy Advance (DB Export) (20221110-045334).xml"
Get the platform ID from the URL, by opening any game for that platform in the Datomatic.
Using our GBA example: https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=0115
The number following the "s=" is the platform ID, here it's 23.
Don't forget to remove the (DB Export) and numbers following the platform name.
So our final filename will be "23 Nintendo - Game Boy Advance.xml"
Do this for each file you'd like to upload, a handful are included as examples.
4. Simply run parseXML.py, ensuring you are running it from the root folder of the repository. Depending on the number of platforms in your xmls folder it may take up to a couple minutes. Not all platforms have been tested and the No-Intro DB files are notoriously inconsistent so please report any errors to CrownRoyal.

Now that you've loaded all your DB files you're ready to install the script itself.
1. By default it will look for a flask server running on localhost. If you are running the database from a different machine that you will be using the userscript on, change the `const server = "http://localhost:5000";` variable at the top of the script to whatever you will be using.
2. Install the script the standard way

The script won't work without a flask server running- this is what lets it access the database. To run the server:
1. Ensure you are in the root folder of the repository or the server will not be able to find all its files.
2. Simply run the file, and leave any windows or terminals open. It is a long running application so if you close the window it opens or is running it it will close the server.

That it! Head over to GGn and try it out.


