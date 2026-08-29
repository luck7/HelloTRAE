"""Export every 16x16 cell from the Battle City sprite sheet as a PNG."""

from pathlib import Path

import pygame


CELL_SIZE = 16
SCALE = 2


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    source = project_root / "images" / "sprite_sheet_nobg.png"
    output_dir = project_root / "images" / "sprites"

    pygame.init()
    sheet = pygame.image.load(source)
    sheet.set_colorkey((0, 0, 1))
    if sheet.get_width() % CELL_SIZE or sheet.get_height() % CELL_SIZE:
        raise ValueError(f"{source} must be divisible into {CELL_SIZE}x{CELL_SIZE} cells.")

    output_dir.mkdir(exist_ok=True)
    columns = sheet.get_width() // CELL_SIZE
    rows = sheet.get_height() // CELL_SIZE

    for row in range(rows):
        for column in range(columns):
            left = column * CELL_SIZE
            top = row * CELL_SIZE
            sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (left, top, CELL_SIZE, CELL_SIZE))
            scaled_sprite = pygame.transform.scale_by(sprite, SCALE)
            pygame.image.save(scaled_sprite, output_dir / f"sprite_r{row + 1:02}_c{column + 1:02}.png")

    print(f"Exported {rows * columns} sprites to {output_dir}")
    pygame.quit()


if __name__ == "__main__":
    main()
