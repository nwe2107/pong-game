import pygame
import random
from dataclasses import dataclass

# --- Config ---
WIDTH, HEIGHT = 800, 600
MARGIN = 30
PADDLE_W, PADDLE_H = 14, 90
BALL_SIZE = 14
BG_COLOR = (16, 18, 22)
FG_COLOR = (235, 235, 235)
ACCENT = (120, 170, 255)
WIN_SCORE = 7
PLAYER_SPEED = 420      # px/s
AI_MAX_SPEED = 360      # px/s
BALL_SPEED = 360        # base px/s

# --- Simple component data classes ---
@dataclass
class Paddle:
    rect: pygame.Rect
    speed: float = 0.0

@dataclass
class Ball:
    rect: pygame.Rect
    vx: float
    vy: float

def reset_ball(to_left: bool = None) -> Ball:
    if to_left is None:
        to_left = random.choice([True, False])
    angle = random.uniform(-0.9, 0.9)  # add some vertical variation
    vx = (-1 if to_left else 1) * BALL_SPEED
    vy = BALL_SPEED * angle
    rect = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    return Ball(rect, vx, vy)

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def draw_center_line(surf):
    dash_h = 18
    gap = 12
    x = WIDTH // 2
    y = 0
    while y < HEIGHT:
        pygame.draw.rect(surf, (60, 64, 72), (x-2, y, 4, dash_h))
        y += dash_h + gap

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Pong")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont(None, 64)
    font_small = pygame.font.SysFont(None, 28)

    # Entities
    player = Paddle(pygame.Rect(MARGIN, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H))
    ai = Paddle(pygame.Rect(WIDTH - MARGIN - PADDLE_W, HEIGHT//2 - PADDLE_H//2, PADDLE_W, PADDLE_H))
    ball = reset_ball()

    # Game state
    player_score = 0
    ai_score = 0
    paused = False

    def serve(scored_left: bool):
        nonlocal ball
        ball = reset_ball(to_left=not scored_left)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds since last frame

        # --- Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_p]:
            paused = not paused
            pygame.time.wait(150)  # debounce
        if keys[pygame.K_r]:
            player_score = 0
            ai_score = 0
            serve(scored_left=False)
            pygame.time.wait(150)

        # --- Update ---
        if not paused:
            # Player movement
            player.speed = (keys[pygame.K_s] - keys[pygame.K_w]) * PLAYER_SPEED  # True=1, False=0
            # (Because booleans act like 1/0, S - W gives -1/0/1)
            player.rect.y += int(player.speed * dt)
            player.rect.y = clamp(player.rect.y, 0, HEIGHT - PADDLE_H)

            # AI movement: track ball with capped speed and a bit of reaction delay
            target_y = ball.rect.centery - PADDLE_H // 2
            dy = target_y - ai.rect.y
            max_step = AI_MAX_SPEED * dt
            if abs(dy) > max_step:
                ai.rect.y += int(max_step if dy > 0 else -max_step)
            else:
                ai.rect.y = target_y
            ai.rect.y = clamp(ai.rect.y, 0, HEIGHT - PADDLE_H)

            # Ball movement
            ball.rect.x += int(ball.vx * dt)
            ball.rect.y += int(ball.vy * dt)

            # Wall collisions (top/bottom)
            if ball.rect.top <= 0:
                ball.rect.top = 0
                ball.vy = -ball.vy
            elif ball.rect.bottom >= HEIGHT:
                ball.rect.bottom = HEIGHT
                ball.vy = -ball.vy

            # Paddle collisions
            if ball.rect.colliderect(player.rect) and ball.vx < 0:
                overlap = player.rect.right - ball.rect.left
                ball.rect.left += overlap
                ball.vx = -ball.vx * 1.04  # a tiny speed-up
                # add spin based on where it hit the paddle + player movement
                offset = (ball.rect.centery - player.rect.centery) / (PADDLE_H / 2)
                ball.vy += (offset * 120) + (player.speed * 0.25)

            if ball.rect.colliderect(ai.rect) and ball.vx > 0:
                overlap = ball.rect.right - ai.rect.left
                ball.rect.right -= overlap
                ball.vx = -ball.vx * 1.04
                offset = (ball.rect.centery - ai.rect.centery) / (PADDLE_H / 2)
                ball.vy += (offset * 120)

            # Scoring (left/right walls)
            if ball.rect.right < 0:
                ai_score += 1
                serve(scored_left=True)
            elif ball.rect.left > WIDTH:
                player_score += 1
                serve(scored_left=False)

        # --- Draw ---
        screen.fill(BG_COLOR)
        draw_center_line(screen)
        pygame.draw.rect(screen, FG_COLOR, player.rect, border_radius=6)
        pygame.draw.rect(screen, FG_COLOR, ai.rect, border_radius=6)
        pygame.draw.rect(screen, ACCENT, ball.rect, border_radius=7)

        # HUD
        score_surf = font_big.render(f"{player_score}   {ai_score}", True, FG_COLOR)
        score_rect = score_surf.get_rect(center=(WIDTH//2, 50))
        screen.blit(score_surf, score_rect)

        if paused:
            p = font_big.render("PAUSED", True, FG_COLOR)
            screen.blit(p, p.get_rect(center=(WIDTH//2, HEIGHT//2)))

        if player_score >= WIN_SCORE or ai_score >= WIN_SCORE:
            msg = "You Win! 🎉" if player_score > ai_score else "AI Wins 🤖"
            info1 = font_big.render(msg, True, FG_COLOR)
            info2 = font_small.render("Press R to restart, Esc to quit", True, FG_COLOR)
            screen.blit(info1, info1.get_rect(center=(WIDTH//2, HEIGHT//2 - 20)))
            screen.blit(info2, info2.get_rect(center=(WIDTH//2, HEIGHT//2 + 28)))

        # Footer help
        help_text = font_small.render("W/S move • P pause • R reset • Esc quit", True, (180, 184, 190))
        screen.blit(help_text, help_text.get_rect(center=(WIDTH//2, HEIGHT - 20)))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()