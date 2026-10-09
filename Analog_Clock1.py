
import pygame
import random
import datetime
import math

# -----------------------------
# Configuration
# -----------------------------
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
CLOCK_RADIUS = 390
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Forest Analog Clock")
clock = pygame.time.Clock()

# Neon color palette
BLACK = (2, 10, 12)
WHITE = (235, 255, 250)
CYAN = (0, 255, 220)
GREEN = (30, 255, 120)
LIME = (180, 255, 70)
RED = (255, 45, 80)
DIM_GREEN = (10, 75, 50)

# -----------------------------
# Pre-rendered forest gradient
# -----------------------------
background = pygame.Surface((WIDTH, HEIGHT))

top_color = (2, 10, 18)
bottom_color = (4, 42, 29)

for y in range(HEIGHT):
    t = y / HEIGHT
    color = tuple(
        int(top_color[i] * (1 - t) + bottom_color[i] * t)
        for i in range(3)
    )
    pygame.draw.line(background, color, (0, y), (WIDTH, y))

# Soft green atmospheric glow
ambient_glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

pygame.draw.ellipse(
    ambient_glow,
    (0, 255, 120, 18),
    (100, 420, 600, 420)
)

pygame.draw.ellipse(
    ambient_glow,
    (0, 180, 255, 12),
    (180, 100, 440, 450)
)

background.blit(ambient_glow, (0, 0))


# -----------------------------
# Stars and animated fireflies
# -----------------------------
stars = []

for _ in range(150):
    stars.append({
        "x": random.randrange(WIDTH),
        "y": random.randrange(HEIGHT),
        "radius": random.choice([1, 1, 1, 2]),
        "phase": random.uniform(0, math.tau)
    })

fireflies = []

for _ in range(40):
    fireflies.append({
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "speed": random.uniform(10, 32),
        "drift": random.uniform(8, 20),
        "phase": random.uniform(0, math.tau),
        "radius": random.choice([2, 2, 3, 4])
    })


# -----------------------------
# Glow drawing helper
# -----------------------------
def draw_glow_line(surface, color, start, end, width):
    """Draw a neon line with a soft outer glow."""
    sx, sy = map(int, start)
    ex, ey = map(int, end)

    # Broad, transparent glow layers
    for extra_width, alpha in [
        (18, 12),
        (12, 22),
        (7, 40)
    ]:
        glow = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        glow_color = (*color, alpha)

        pygame.draw.line(
            glow,
            glow_color,
            (sx, sy),
            (ex, ey),
            width + extra_width
        )

        surface.blit(glow, (0, 0))

    # Bright center line
    pygame.draw.line(
        surface, color, (sx, sy), (ex, ey), width
    )


def draw_glow_circle(surface, color, position, radius, width=2):
    """Draw a circle with layered neon glow."""
    x, y = map(int, position)

    for extra, alpha in [(14, 12), (9, 25), (4, 55)]:
        glow = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (*color, alpha),
            (x, y),
            radius + extra,
            max(1, width + 2)
        )

        surface.blit(glow, (0, 0))

    pygame.draw.circle(
        surface, color, (x, y), radius, width
    )


# -----------------------------
# Clock geometry
# -----------------------------
def polar_to_cartesian(radius, angle):
    radians = math.radians(angle)

    x = CENTER[0] + radius * math.sin(radians)
    y = CENTER[1] - radius * math.cos(radians)

    return x, y


# -----------------------------
# Text drawing
# -----------------------------
font_cache = {}


def get_font(size):
    if size not in font_cache:
        font_cache[size] = pygame.font.SysFont(
            "Arial", size, bold=True
        )
    return font_cache[size]


def draw_text(text, size, position, color=WHITE):
    font = get_font(size)
    rendered = font.render(str(text), True, color)
    rect = rendered.get_rect(center=position)
    screen.blit(rendered, rect)


# -----------------------------
# Animated nature background
# -----------------------------
def draw_nature_background(elapsed, dt):
    screen.blit(background, (0, 0))

    # Twinkling stars
    for star in stars:
        pulse = (
            math.sin(elapsed * 1.8 + star["phase"]) + 1
        ) / 2

        color = (
            int(35 + 100 * pulse),
            int(110 + 120 * pulse),
            int(100 + 140 * pulse)
        )

        pygame.draw.circle(
            screen,
            color,
            (int(star["x"]), int(star["y"])),
            star["radius"]
        )

    # Drifting fireflies
    for fly in fireflies:
        fly["y"] -= fly["speed"] * dt
        fly["x"] += (
            math.sin(elapsed * 0.8 + fly["phase"])
            * fly["drift"] * dt
        )

        if fly["y"] < -10:
            fly["y"] = HEIGHT + 10
            fly["x"] = random.uniform(0, WIDTH)

        if fly["x"] < 0:
            fly["x"] = WIDTH
        elif fly["x"] > WIDTH:
            fly["x"] = 0

        pulse = (
            math.sin(elapsed * 3 + fly["phase"]) + 1
        ) / 2

        if pulse > 0.15:
            x, y = int(fly["x"]), int(fly["y"])
            radius = fly["radius"]

            # Compact glow to avoid creating full-screen surfaces
            glow_size = radius * 6
            glow = pygame.Surface(
                (glow_size * 2 + 1, glow_size * 2 + 1),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (80, 255, 110, int(15 + 35 * pulse)),
                (glow_size, glow_size),
                glow_size
            )

            screen.blit(
                glow, (x - glow_size, y - glow_size)
            )

            pygame.draw.circle(
                screen,
                (int(100 + 100 * pulse), 255, int(70 + 100 * pulse)),
                (x, y),
                radius
            )


# -----------------------------
# Neon clock face
# -----------------------------
def draw_clock_face(elapsed):
    # Outer glowing rings
    draw_glow_circle(
        screen, GREEN, CENTER, CLOCK_RADIUS - 10, 3
    )

    draw_glow_circle(
        screen, CYAN, CENTER, CLOCK_RADIUS - 23, 1
    )

    # Neon minute and hour ticks
    for angle in range(0, 360, 6):
        if angle % 30 == 0:
            inner_radius = CLOCK_RADIUS - 58
            color = GREEN
            width = 4
        else:
            inner_radius = CLOCK_RADIUS - 35
            color = (30, 140, 110)
            width = 2

        start = polar_to_cartesian(
            CLOCK_RADIUS - 29, angle
        )
        end = polar_to_cartesian(
            inner_radius, angle
        )

        pygame.draw.line(
            screen, color, start, end, width
        )

    # Clock numbers
    for number in range(1, 13):
        pos = polar_to_cartesian(
            CLOCK_RADIUS - 92, number * 30
        )

        color = CYAN if number % 3 == 0 else WHITE

        # Small neon halo behind each number
        draw_text(number, 80, pos, DIM_GREEN)
        draw_text(number, 76, pos, color)

    # Current date and calendar data
    now = datetime.datetime.now()

    weekday_names = {
        1: "Mo", 2: "Tu", 3: "We", 4: "Th",
        5: "Fr", 6: "Sa", 7: "Su"
    }

    month_names = {
        1: "JAN", 2: "FEB", 3: "MAR", 4: "APR",
        5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG",
        9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"
    }

    # Weekday, ISO week number, month, day, year
    boxes = [
        (WIDTH // 2 - 220, HEIGHT // 2, "weekday"),
        (WIDTH // 2 - 140, HEIGHT // 2, "week"),
        (WIDTH // 2 + 140, HEIGHT // 2, "month"),
        (WIDTH // 2 + 220, HEIGHT // 2, "day"),
        (WIDTH // 2, HEIGHT // 2 + 160, "year")
    ]

    for x, y, label in boxes:
        box_width = 100 if label == "year" else 80
        box_height = 60

        rect = pygame.Rect(
            x - box_width // 2,
            y - box_height // 2,
            box_width,
            box_height
        )

        color = CYAN if label in ("weekday", "month") else GREEN

        draw_glow_circle(
            screen, color, rect.center, 2, 1
        )

        # Thin neon rectangle
        pygame.draw.rect(screen, color, rect, 1)

    draw_text(
        weekday_names[now.isoweekday()],
        36,
        (WIDTH // 2 - 220, HEIGHT // 2),
        WHITE
    )

    draw_text(
        now.isocalendar().week,
        36,
        (WIDTH // 2 - 140, HEIGHT // 2),
        CYAN
    )

    draw_text(
        month_names[now.month],
        36,
        (WIDTH // 2 + 140, HEIGHT // 2),
        WHITE
    )

    draw_text(
        f"{now.day:02d}",
        36,
        (WIDTH // 2 + 220, HEIGHT // 2),
        CYAN
    )

    draw_text(
        now.year,
        36,
        (WIDTH // 2, HEIGHT // 2 + 160),
        GREEN
    )

    # Smooth current time
    seconds = now.second + now.microsecond / 1_000_000
    minutes = now.minute + seconds / 60
    hours = (now.hour % 12) + minutes / 60

    # Hour hand: neon green
    hour_angle = hours * 30
    draw_glow_line(
        screen,
        GREEN,
        CENTER,
        polar_to_cartesian(205, hour_angle),
        12
    )

    # Minute hand: cyan
    minute_angle = minutes * 6
    draw_glow_line(
        screen,
        CYAN,
        CENTER,
        polar_to_cartesian(275, minute_angle),
        8
    )

    # Second hand: bright red
    second_angle = seconds * 6
    draw_glow_line(
        screen,
        RED,
        CENTER,
        polar_to_cartesian(330, second_angle),
        3
    )

    # Center hub
    draw_glow_circle(screen, CYAN, CENTER, 12, 4)
    pygame.draw.circle(screen, WHITE, CENTER, 4)


# -----------------------------
# Main loop
# -----------------------------
def main():
    running = True
    elapsed = 0.0

    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_nature_background(elapsed, dt)
        draw_clock_face(elapsed)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()