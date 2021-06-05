<div align=center>
    <h1>AssBot (open-source Ebobot)</h1>
</div>

<div align=center>
    <h2>Description</h2>
    <p>This bot is like "Ebobot" @kraft28_bot but that's open-source was written on Python.</p>
</div>

<div>
    <div>
        <h3>Files:</h3>
        <ul>
            <li><b>config.py</b> — file with configuration parameters (TOKEN, SUPER_USERS, DEBUG)</li>
            <li><b>main.py</b> — main file</li>
        </ul>
    </div>
    <div align=center>
        <h3>Recommended Python version: Python 3.9.5</h3>
    </div>
    <div>
        <h3>Modules in use:</h3>
    </div>
    <ul>
        <li><b>json</b></li>
        <li><b>random</b></li>
        <li><b>sqlite3</b></li>
        <li><b>os</b></li>
        <li><b>time</b></li>
        <li><b>aiogram</b></li>
    </ul>
</div>

<div>
    <div>
        <h3>User commands:</h3>
    </div>
    <div>
        <ul>
            <li>
                <b>/ass</b> — start playing
            </li>
            <li>
                <b>/help</b> — show help message
            </li>
            <li>
                <b>/leave</b> — leave game and delete user's data
            </li>
            <li>
                <b>/r {text}</b> — send report to `reports` table
            </li>
            <li>
                <b>/statistic</b> — show top list of users
            </li>
        </ul>
    </div>
    <div>
        <h3>Admin's commands:</h3>
    </div>
    <div>
        <ul>
            <li>
                <b>/blacklist</b> — show banned users
            </li>
            <li>
                <b>/ub {user_id}</b> — unban user
            </li>
            <li>
                <b>/show_reports</b> — show all reports from table `reports`
            </li>
            <li>
                <b>/clear_reports</b> — delete all rows in table `reports`
            </li>
        </ul>
    </div>
</div>
