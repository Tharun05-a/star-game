
import tkinter as tk
import random
import math

# ==========================
# CATCH THE FALLING STARS
# ==========================

WIDTH = 800
HEIGHT = 600

root = tk.Tk()
root.title("Catch the Falling Stars")
root.resizable(False, False)

canvas = tk.Canvas(
    root, width=WIDTH, height=HEIGHT,
    bg="#07152f", highlightthickness=0
)
canvas.pack()

# Game variables
score = 0
lives = 3
game_over = False
started = False
player_x = WIDTH // 2
player_y = HEIGHT - 75
player_speed = 8
objects = []
particles = []
keys = set()
frame = 0
high_score = 0

# Starry background
background_stars = []
for i in range(90):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.choice([1, 2, 2, 3])
    background_stars.append(
        canvas.create_oval(
            x, y, x + size, y + size,
            fill="white", outline=""
        )
    )

# HUD
canvas.create_text(
    20, 22, text="STAR CATCHER",
    fill="#60eaff", font=("Arial", 17, "bold"),
    anchor="w"
)
score_text = canvas.create_text(
    WIDTH - 20, 22, text="Score: 0",
    fill="white", font=("Arial", 17, "bold"),
    anchor="e"
)
lives_text = canvas.create_text(
    20, 53, text="Lives: ♥ ♥ ♥",
    fill="#ff5c82", font=("Arial", 14, "bold"),
    anchor="w"
)

# Player spaceship
def draw_player():
    x = player_x
    y = player_y

    # Animated engine flame
    flame = random.randint(8, 19)
    canvas.create_polygon(
        x - 10, y + 18,
        x, y + 18 + flame,
        x + 10, y + 18,
        fill=random.choice(["#ff9f43", "#ffe66d", "#ff5c82"]),
        outline=""
    )

    # Ship body
    canvas.create_polygon(
        x, y - 24,
        x - 24, y + 18,
        x - 11, y + 13,
        x, y + 18,
        x + 11, y + 13,
        x + 24, y + 18,
        fill="#48d9ff", outline="white", width=2
    )

    # Cockpit
    canvas.create_oval(
        x - 7, y - 12, x + 7, y + 3,
        fill="#f4fdff", outline="#a0f0ff"
    )

# Spawn a falling object
def spawn_object():
    x = random.randint(30, WIDTH - 30)
    y = -25

    if random.random() < 0.72:
        kind = "star"
        color = "#ffd84d"
        size = 15
        speed = random.uniform(2.5, 4.5) + score * 0.025
    else:
        kind = "meteor"
        color = "#ff526e"
        size = 19
        speed = random.uniform(3, 5) + score * 0.025

    obj_id = canvas.create_oval(
        x - size, y - size, x + size, y + size,
        fill=color, outline="white", width=1
    )

    # Stars get a glowing-looking center
    if kind == "star":
        inner = canvas.create_text(
            x, y, text="★", fill="#fff8c2",
            font=("Arial", 17, "bold")
        )
    else:
        inner = canvas.create_text(
            x, y, text="✦", fill="#851d46",
            font=("Arial", 15, "bold")
        )

    objects.append({
        "x": x, "y": y, "size": size,
        "speed": speed, "kind": kind,
        "body": obj_id, "inner": inner
    })

# Sparkle particles
def burst(x, y, color):
    for i in range(10):
        angle = random.random() * math.pi * 2
        speed = random.uniform(1, 4)
        dot = canvas.create_oval(
            x, y, x + 5, y + 5,
            fill=color, outline=""
        )
        particles.append({
            "id": dot,
            "x": x, "y": y,
            "dx": math.cos(angle) * speed,
            "dy": math.sin(angle) * speed,
            "life": 16
        })

# Keyboard controls
def key_down(event):
    global started
    key = event.keysym.lower()
    keys.add(key)

    if key in ("left", "right", "a", "d", "space"):
        started = True

    if key == "r" and game_over:
        restart()

def key_up(event):
    keys.discard(event.keysym.lower())

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

# Restart game
def restart():
    global score, lives, game_over, started
    global player_x, objects, particles, frame

    for obj in objects:
        canvas.delete(obj["body"])
        canvas.delete(obj["inner"])

    for p in particles:
        canvas.delete(p["id"])

    objects.clear()
    particles.clear()

    score = 0
    lives = 3
    game_over = False
    started = True
    player_x = WIDTH // 2
    frame = 0
    keys.clear()

    canvas.itemconfig(score_text, text="Score: 0")
    canvas.itemconfig(lives_text, text="Lives: ♥ ♥ ♥")

    canvas.delete("overlay")
    update()

# Main animation loop
def update():
    global score, lives, game_over, frame, player_x

    canvas.delete("player")
    frame += 1

    # Twinkle background stars
    if frame % 8 == 0:
        star_id = random.choice(background_stars)
        color = random.choice(["white", "#6384b8", "#a4eaff"])
        canvas.itemconfig(star_id, fill=color)

    if game_over:
        return

    # Move player
    if "left" in keys or "a" in keys:
        player_x -= player_speed
    if "right" in keys or "d" in keys:
        player_x += player_speed

    player_x = max(28, min(WIDTH - 28, player_x))

    # Spawn objects
    if started and frame % max(18, 42 - score // 4) == 0:
        spawn_object()

    # Animate falling objects
    for obj in objects[:]:
        obj["y"] += obj["speed"]
        obj["x"] += math.sin(frame * 0.04 + obj["y"] * 0.02) * 1.2

        x = obj["x"]
        y = obj["y"]
        size = obj["size"]

        canvas.coords(
            obj["body"], x-size, y-size, x+size, y+size
        )
        canvas.coords(obj["inner"], x, y)

        # Collision with spaceship
        hit = (
            abs(x - player_x) < size + 20
            and abs(y - player_y) < size + 15
        )

        if hit:
            canvas.delete(obj["body"])
            canvas.delete(obj["inner"])
            objects.remove(obj)

            if obj["kind"] == "star":
                score += 1
                burst(x, y, "#ffd84d")
                canvas.itemconfig(
                    score_text, text="Score: " + str(score)
                )
            else:
                lives -= 1
                burst(x, y, "#ff526e")
                hearts = " ".join(["♥"] * lives)
                canvas.itemconfig(
                    lives_text, text="Lives: " + hearts
                )

                if lives <= 0:
                    end_game()
                    return

        elif y > HEIGHT + 30:
            canvas.delete(obj["body"])
            canvas.delete(obj["inner"])
            objects.remove(obj)

    # Animate particles
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1

        canvas.coords(
            p["id"], p["x"], p["y"],
            p["x"] + 5, p["y"] + 5
        )

        if p["life"] <= 0:
            canvas.delete(p["id"])
            particles.remove(p)

    # Draw player on top of the background
    draw_player()

    # Start screen instructions
    if not started:
        canvas.delete("overlay")
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 45,
            text="CATCH THE STARS!",
            fill="#ffe66d", font=("Arial", 30, "bold"),
            tags="overlay"
        )
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 5,
            text="Move with ← → or A / D",
            fill="white", font=("Arial", 17),
            tags="overlay"
        )
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 40,
            text="Catch GOLD stars • Avoid RED meteors",
            fill="#a9c9ff", font=("Arial", 13),
            tags="overlay"
        )
        canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 80,
            text="Press an arrow key to start",
            fill="#60eaff", font=("Arial", 14, "bold"),
            tags="overlay"
        )

    root.after(16, update)

def end_game():
    global game_over
    game_over = True

    canvas.create_rectangle(
        130, 190, WIDTH - 130, 410,
        fill="#101b3a", outline="#60eaff",
        width=3, tags="overlay"
    )
    canvas.create_text(
        WIDTH // 2, 245,
        text="GAME OVER",
        fill="#ff5c82", font=("Arial", 32, "bold"),
        tags="overlay"
    )
    canvas.create_text(
        WIDTH // 2, 300,
        text="Final Score: " + str(score),
        fill="white", font=("Arial", 22, "bold"),
        tags="overlay"
    )
    canvas.create_text(
        WIDTH // 2, 350,
        text="Press R to play again",
        fill="#60eaff", font=("Arial", 16),
        tags="overlay"
    )

# Start the game
update()
root.mainloop()
