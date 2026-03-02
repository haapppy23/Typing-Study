import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -------------------------
# Ant Foraging Emergence (simple)
# - Agents follow local pheromone gradient + randomness
# - Drop pheromone when carrying food
# - Pheromone evaporates + diffuses
# - Emergent trails form between nest and food
# -------------------------

rng = np.random.default_rng(42)

# World settings
H, W = 120, 160
N_ANTS = 250
STEPS_PER_FRAME = 5

# Pheromone fields
pher_food = np.zeros((H, W), dtype=np.float32)   # "go to food" pheromone (laid by ants returning home)
pher_home = np.zeros((H, W), dtype=np.float32)   # "go to home" pheromone (laid by ants going to food)

EVAP = 0.02        # evaporation rate
DIFF = 0.20        # diffusion strength (0..1-ish)
DROP = 1.5         # pheromone drop amount
MAX_PHER = 50.0    # clamp

# Movement / sensing
SENSE_RADIUS = 2
RANDOM_TURN = 0.25  # higher => more random wandering
FOLLOW_BIAS = 1.8   # higher => stronger pheromone following

# Nest and Food
nest = np.array([H // 2, W // 4], dtype=np.int32)
food = np.array([H // 2, (W * 3) // 4], dtype=np.int32)
FOOD_RADIUS = 8
NEST_RADIUS = 6

# Obstacles (optional)
obstacles = np.zeros((H, W), dtype=bool)
# Example wall with a gap (uncomment to see interesting paths)
# obstacles[H//2 - 25:H//2 + 25, W//2] = True
# obstacles[H//2 - 3:H//2 + 3, W//2] = False  # gap

# Ant states
# pos: (N,2), dir: (N,2) continuous, carrying: bool
pos = np.repeat(nest[None, :], N_ANTS, axis=0).astype(np.int32)
dirs = rng.normal(size=(N_ANTS, 2))
dirs = dirs / (np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-9)
carrying = np.zeros(N_ANTS, dtype=bool)

food_collected = 0

def in_bounds(p):
    return (0 <= p[0] < H) and (0 <= p[1] < W)

def clamp_pos(p):
    p[0] = np.clip(p[0], 0, H - 1)
    p[1] = np.clip(p[1], 0, W - 1)
    return p

def near(a, b, r):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2 <= r*r

def diffuse(field):
    # simple 4-neighbor diffusion
    up = np.roll(field, -1, axis=0)
    down = np.roll(field, 1, axis=0)
    left = np.roll(field, -1, axis=1)
    right = np.roll(field, 1, axis=1)
    field[:] = (1 - DIFF) * field + (DIFF / 4.0) * (up + down + left + right)

def evaporate(field):
    field *= (1.0 - EVAP)
    np.clip(field, 0.0, MAX_PHER, out=field)

def sample_field(field, p):
    return field[p[0], p[1]]

def choose_direction(i):
    """
    Local rule:
    - If carrying food: follow pher_home gradient to nest; deposit pher_food
    - Else: follow pher_food gradient to food; deposit pher_home
    """
    global food_collected

    p = pos[i].copy()

    # Determine target field to follow
    follow = pher_home if carrying[i] else pher_food

    # Sense in a small neighborhood and move toward higher pheromone (gradient-ish)
    best_score = -1e9
    best_vec = None

    # Candidate directions: forward-ish + random samples
    # We'll create a few candidate vectors and pick the best
    candidates = []

    # Forward direction
    candidates.append(dirs[i])

    # A few noisy directions around current dir
    for _ in range(6):
        v = dirs[i] + rng.normal(scale=0.6, size=2)
        n = np.linalg.norm(v)
        if n > 1e-9:
            candidates.append(v / n)

    # Also add slight attraction to goal (nest/food) to help early formation
    goal = nest if carrying[i] else food
    g = goal.astype(float) - p.astype(float)
    gn = np.linalg.norm(g)
    if gn > 1e-9:
        candidates.append((g / gn) * 0.7 + dirs[i] * 0.3)

    for v in candidates:
        # sense point ahead
        sp = p + np.round(v * SENSE_RADIUS).astype(np.int32)
        sp = clamp_pos(sp)

        if obstacles[sp[0], sp[1]]:
            continue

        pher = sample_field(follow, sp)
        # Combine pheromone following with a bit of random exploration
        score = FOLLOW_BIAS * pher - RANDOM_TURN * rng.random()
        if score > best_score:
            best_score = score
            best_vec = v

    if best_vec is None:
        # stuck: random turn
        best_vec = rng.normal(size=2)
        best_vec /= (np.linalg.norm(best_vec) + 1e-9)

    return best_vec

def step():
    global food_collected

    # Update ants
    for i in range(N_ANTS):
        # Pick direction based on local rule
        d = choose_direction(i)
        dirs[i] = 0.7 * dirs[i] + 0.3 * d
        dirs[i] /= (np.linalg.norm(dirs[i]) + 1e-9)

        # Move 1 cell
        newp = pos[i] + np.round(dirs[i]).astype(np.int32)
        newp = clamp_pos(newp)

        if obstacles[newp[0], newp[1]]:
            # bounce: turn around-ish
            dirs[i] *= -1
            continue

        pos[i] = newp

        # Pick up / drop food
        if not carrying[i] and near(pos[i], food, FOOD_RADIUS):
            carrying[i] = True

        if carrying[i] and near(pos[i], nest, NEST_RADIUS):
            carrying[i] = False
            food_collected += 1

        # Deposit pheromones:
        # - when going to food (not carrying): drop "home" pheromone
        # - when returning home (carrying): drop "food" pheromone
        if carrying[i]:
            pher_food[pos[i][0], pos[i][1]] = min(MAX_PHER, pher_food[pos[i][0], pos[i][1]] + DROP)
        else:
            pher_home[pos[i][0], pos[i][1]] = min(MAX_PHER, pher_home[pos[i][0], pos[i][1]] + DROP)

    # Update pheromone fields (diffuse + evaporate)
    diffuse(pher_food); evaporate(pher_food)
    diffuse(pher_home); evaporate(pher_home)

# -------------------------
# Visualization
# -------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Ant Emergence: trails form via local rules (pheromones)")
ax.set_xticks([]); ax.set_yticks([])

# Background: show combined pheromone intensity
img = ax.imshow(pher_food + pher_home, vmin=0, vmax=MAX_PHER, interpolation="nearest")

# Obstacles overlay
if obstacles.any():
    obs_y, obs_x = np.where(obstacles)
    ax.scatter(obs_x, obs_y, s=2, marker='s')

# Nest & food markers
ax.scatter([nest[1]], [nest[0]], s=80, marker="o", label="Nest")
ax.scatter([food[1]], [food[0]], s=80, marker="*", label="Food")

# Ant dots
ants_scatter = ax.scatter(pos[:, 1], pos[:, 0], s=6)

info = ax.text(0.01, 0.99, "", transform=ax.transAxes, va="top")

ax.legend(loc="lower right")

def update(frame):
    for _ in range(STEPS_PER_FRAME):
        step()

    img.set_data(pher_food + pher_home)
    ants_scatter.set_offsets(np.c_[pos[:, 1], pos[:, 0]])
    info.set_text(f"Food delivered: {food_collected}")
    return img, ants_scatter, info

ani = FuncAnimation(fig, update, interval=30, blit=False)
plt.show()
