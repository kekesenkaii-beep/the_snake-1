from random import choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Слоаврь-константа со след.направлениями движения:
DIRECTIONS_MAP = {
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Константы скорости:
SPEED = 20
FAST_SPEED = 30

BOARD_BACKGROUND_COLOR = (128, 128, 128)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс каждого игрового объекта (змейка, яблоко)."""

    def __init__(self, color=None) -> None:
        self.body_color = color
        self.position = CENTER

    def draw_cell(self, position, color=None):
        """Базовая зарисовка ячейки."""
        if color is None:
            color = self.body_color

        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Базовый метод отрисовки объекта (переопределяется в потомках)."""


class Apple(GameObject):
    """Дочерний класс, базового игрового объекта — Яблоко."""

    def __init__(self, forbidden_cells=(), color=APPLE_COLOR):
        super().__init__(color)
        self.randomize_position(forbidden_cells)

    def randomize_position(self, forbidden_cells):
        """Метод, отвечает за рандомную позицию каждого "нового" яблока."""
        self.position = choice(tuple(ALL_CELLS - set(forbidden_cells)))

    def draw(self):
        """Отрисовка яблока."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """
    Дочерний класс, базового игрового объекта — Змейка,
    дополненный аргументами: длина, направление.
    """

    def __init__(self, color=SNAKE_COLOR):
        super().__init__(color)
        self.reset()

    def draw(self):
        """Отрисовка змейки."""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def move(self):
        """Метод расчета новой головы по заданному направлению."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))

        self.last = (
            self.positions.pop() if len(self.positions) > self.lenght else None
        )

    def reset(self):
        """Метод сброса игры до стартовых значений."""
        self.lenght = 1
        self.direction = LEFT
        self.positions = [CENTER]
        self.last = None

    def get_head_position(self) -> tuple:
        """Обработка запроса, а где голова?"""
        return self.positions[0]

    def update_direction(self):
        """Добавление метода пустого для pytest."""


class Backend:
    """
    Отдельный класс бэкэнда.
    Обработка файлов, возврат рекордного кол-ва очков.
    """

    def __init__(self):
        self.file_name = 'result.txt'

    def save_score(self, score: int) -> None:
        """Обработка файла, записываем очки."""
        with open(self.file_name, 'a', encoding='utf-8') as file:
            file.write(f'{score}\n')

    def get_best_score(self) -> int:
        """Обработка файла, возвращаем рекорд."""
        best_score = 0
        with open(self.file_name, 'r', encoding='utf-8') as file:
            for line in file:
                score = int(line.strip())
                if score > best_score:
                    best_score = score
        return best_score


def handle_keys(snake):
    """Метод обработки нажатий клавиатуры и обновления направления."""
    for event in pg.event.get():
        if (
            event.type == pg.QUIT
            or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)
        ):
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:
            snake.direction = DIRECTIONS_MAP.get(
                (snake.direction, event.key),
                snake.direction
            )

    pressed = pg.key.get_pressed()
    return pressed[pg.K_SPACE]


def main():
    """Главная функция игры, запуск игрового цикла, логика."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple(snake.positions)
    backend = Backend()
    score = 1
    speed = SPEED

    while True:
        fast = handle_keys(snake)
        speed = FAST_SPEED if fast else SPEED
        clock.tick(speed)
        snake.move()

        if apple.position == snake.get_head_position():
            snake.lenght += 1
            score += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            backend.save_score(score)
            snake.reset()
            score = 1
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()

        record_score = backend.get_best_score()
        pg.display.set_caption(
            '"Змейка". "ESC" - выход "SPACE" - ускорение.'
            f'Очки: {score} Рекорд: {record_score}.'
        )
        pg.display.update()


if __name__ == '__main__':
    main()
