# 🚨 EMERGENCY VIVA SURVIVAL GUIDE — Read Only This

---

## WHAT DOES YOUR PROJECT DO? (Memorize this)

> "SkillArena is a chess analytics platform. A player imports their chess games, we store every move in the database, an ML model analyzes their weaknesses, and we recommend practice drills to improve."

That's it. That's the whole project.

---

## YOUR 8 TABLES (just remember what each one STORES)

1. **players** — username, email, password, elo rating
2. **matches** — each chess game (who played, result, opening name, date)
3. **moves** — every single move in every game (move notation, evaluation score, was it a blunder?)
4. **move_annotations** — engine comments on moves (blunder/brilliant/best_move)
5. **weakness_reports** — ML-generated report (blunder rate, accuracy, weak areas)
6. **drills** — practice puzzles (chess position + correct answer)
7. **drill_attempts** — player's attempts at drills (correct or wrong, time taken)
8. **recommendations** — links a player's weakness report to suggested drills

---

## 5 IMPRESSIVE THINGS TO MENTION (say these yourself, don't wait to be asked)

1. **"We used Range Partitioning"** — matches and moves are split into monthly sub-tables. So when you search for June games, only the June table is scanned, not the entire history.

2. **"We have a Materialized View"** — the leaderboard stats (win rate, games played) are pre-calculated and stored. It loads instantly instead of computing every time.

3. **"We have a Database Trigger"** — whenever a new game is imported, a trigger automatically creates a weakness report. No manual step needed.

4. **"We used Partial Indexing"** — only blunder moves are indexed. Since only 5% of moves are blunders, the index is 20x smaller and faster.

5. **"We used JSONB columns"** — ML output is stored as JSON in the database because the structure can change without needing schema migrations.

---

## THE 10 QUESTIONS HE WILL ASK + YOUR ANSWERS

### 1. "Explain your project"
> "It's a chess analytics platform. Players import games from Lichess or Chess.com. We store every move, analyze them using KMeans clustering to find weakness patterns, and recommend targeted practice drills."

### 2. "How many tables? What's the relationship?"
> "8 tables. A player has many matches. Each match has many moves. Each move can have annotations. A player has weakness reports. Based on the report, we recommend drills. The recommendations table connects player, report, and drill — it's a junction table."

### 3. "What is normalization? Is your schema normalized?"
> "Normalization removes redundant data. Our schema is in BCNF — every column depends only on the primary key. We have one intentional denormalization — JSONB columns for ML output — to avoid extra tables and joins."

### 4. "What is a primary key? Foreign key?"
> "Primary key uniquely identifies each row — we use UUIDs. Foreign key references another table's primary key. For example, matches.player_id references players.id. We use ON DELETE CASCADE so deleting a player removes all their data."

### 5. "Why UUID instead of auto-increment?"
> "Security — auto-increment IDs are guessable. UUID is random, so attackers can't enumerate records."

### 6. "What is partitioning?"
> "Splitting a large table into smaller pieces by date range. Our matches table has 36 monthly partitions. When querying last month's games, PostgreSQL only scans 1 partition instead of all data. This is called partition pruning."

### 7. "What is a trigger?"
> "A function that runs automatically on an event. Our trigger runs AFTER INSERT on matches — it auto-creates a weakness report for the player."

### 8. "What is a materialized view?"
> "A stored result of a query. Unlike a normal view which re-runs the query each time, a materialized view stores the data physically. Ours pre-computes player stats for the leaderboard. We refresh it periodically."

### 9. "What is indexing?"
> "An index is like a book's index — it lets the database find rows without scanning everything. We have a partial index on blunders — it only indexes the 5% of moves that are blunders, making it much smaller and faster."

### 10. "Explain ACID properties in your project"
> "Atomicity — importing a game inserts match + all moves in one transaction, if anything fails everything rolls back. Consistency — CHECK constraints ensure only valid data enters. Isolation — each user's request runs in its own transaction. Durability — committed data survives crashes."

---

## WHEN YOU DON'T KNOW SOMETHING

### Use these exact phrases:

**Option 1 — Bridge to something you know:**
> "That's a great question. In our project, what we focused on was [say something from above]..."

**Option 2 — Be honest but smart:**
> "I'd need to verify the exact details, but from what I understand, it works similar to [something you know]..."

**Option 3 — Redirect to your strength:**
> "I can show you how we implemented that in our database — would you like me to pull up the schema?"

---

## IF HE SAYS "SHOW ME THE DATABASE"

Open terminal, type:
```
docker exec -it skillarena-db psql -U skillarena -d skillarena
```

Then type these one by one:
```sql
\dt                          -- shows all tables
\dt matches_*                -- shows partitions (IMPRESSIVE)
SELECT * FROM player_stats_mv;  -- shows materialized view
\df fn_create_pending_report    -- shows trigger function
```

---

## THE ONE RULE

**Always answer with your project's table/column names.** Don't give textbook answers. Say "in our matches table..." not "in a table...". This makes it sound like YOU built it.
