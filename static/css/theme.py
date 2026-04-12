:root {
    --bg: #f8fafc;
    --text: #1e293b;
    --card: #ffffff;
}

body.dark {
    --bg: #020617;
    --text: #e5e7eb;
    --card: #020617;
}

body {
    background: var(--bg);
    color: var(--text);
    transition: background 0.3s ease, color 0.3s ease;
}

.profile-card,
.card,
header {
    background: var(--card);
}

/* Dark Theme */
body.dark-theme {
    --bg: #0f172a;
    --white: #020617;
    --text: #e5e7eb;
    --gray: #1e293b;
    --card-shadow: 0 10px 25px rgba(0,0,0,0.6);

    background-color: var(--bg);
    color: var(--text);
}
