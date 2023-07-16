import arcade
import arcade.gui
# Ширина и высота экрана
SCREEN_WIDTH = 444
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Starship war bom bom"
# Здоровье игрока
HP = 10
HP_SCALING = 0.5
SHOOT_SCALING = 0.5
# Масштабирование спрайтов
CHARACTER_SCALING = 1
SPRITE_SCALING_LASER = 1
TILE_SCALING = 1
# Константы для снарядов
BULLET_SPEED = 8
BULLET_ENEMY_SPEED = 4
SHOOT_INTERVAL = 0.2
SHOOT_ENEMY_INTERVAL = 1.5
# Константы скорости
PERMANENT_SPEED = 1.5
SPEED_PLAYER_Y = 8
SPEED_PLAYER_X = 8
PLAYER_UP_SPEED = SPEED_PLAYER_Y
PLAYER_DOWN_SPEED = SPEED_PLAYER_Y
PLAYER_LEFT_SPEED = SPEED_PLAYER_X
PLAYER_RIGHT_SPEED = SPEED_PLAYER_X


class MyGame(arcade.Window):

    def __init__(self):
        # рекорды
        # Загрузка окна игры
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.tile_map = None
        self.scene = None
        # These are 'lists' that keep track of our sprites. Each sprite should
        # Объявление спрайт листов
        self.player_list = None
        self.bullet_list = None
        self.explosion_list = None
        self.bullet_enemy_list = None
        self.hp_bar_list = None
        # Объявление спрайтов
        self.player_sprite = None
        self.shoot_sprite = None
        self.hp_bar_sprite = None
        self.back_sprite = None
        self.back_list = None
        self.shoot_sprite_list = None
        # Основная камера
        self.camera = None
        # камера для GUI элементов
        self.gui_camera = None
        self.camera_max = 0
        # For the better movement
        self.key_right_pressed = False
        self.key_left_pressed = False
        self.key_up_pressed = False
        self.key_down_pressed = False
        self.key_space_pressed = False
        # collision
        self.collideup = False
        self.collidedown = False
        self.collideleft = False
        self.collideright = False
        self.timer = 0
        self.shoot_timer_player = 0
        self.shoot_timer_enemy = 0
        self.big_shoot_timer = 0
        self.explosion_time = 0
        self.explosion_counter = 0
        self.explosion_numbers = [0, 0]
        self.shoot_numbers = [0, 0]
        self.player_up = PLAYER_UP_SPEED
        self.player_down = PLAYER_DOWN_SPEED
        self.player_left = PLAYER_LEFT_SPEED
        self.player_right = PLAYER_RIGHT_SPEED

        self.screen.center_x = 0
        self.screen.center_y = 0
        self.damage = 0

        self.player_sprite_images = []

        self.score = 0

    def setup(self):
        # Загрузка камеры
        self.camera = arcade.Camera(self.width, self.height)

        # камера для счёта игрока и спрайтов здоровья
        self.gui_camera = arcade.Camera(self.width, self.height)
        # Создание спрайт-листов
        self.explosion_list = arcade.SpriteList()
        explosion = arcade.Sprite("images/explosion.png", TILE_SCALING)
        explosion.center_x = -100
        explosion.center_y = -100
        self.explosion_list.append(explosion)
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.bullet_enemy_list = arcade.SpriteList()
        self.hp_bar_list = arcade.SpriteList()
        self.back_list = arcade.SpriteList()
        self.back_sprite = arcade.Sprite("images/back_ground2.jpg")
        self.back_sprite.center_y = SCREEN_HEIGHT / 1.5
        self.back_sprite.center_x = 222
        self.back_list.append(self.back_sprite)
        self.shoot_sprite_list = arcade.SpriteList()
        shoot = arcade.Sprite("images/shoot.png", SHOOT_SCALING)
        shoot.center_x = -100
        shoot.center_y = -100
        self.shoot_sprite_list.append(shoot)

        # расположение карты
        map_name = "map/map.tmj"
        # слои карты
        layer_options = {
            "guys": {
                "use_spatial_hash": True,
            },
            "coin": {
                "use_spatial_hash": True,
            },
        }

        # Чтение карты игры и использование её в сцене
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # установка спрайта игрока
        image_source = "images/hero.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 222
        self.player_sprite.center_y = 16
        self.player_list.append(self.player_sprite)
        for block in self.scene["guys"]:
            block.set_hit_box = 64
        # hp bar
        for i in range(HP):
            self.hp_bar_sprite = arcade.Sprite("images/full_hp_bar.png", HP_SCALING)
            self.hp_bar_sprite.center_x = 10 + i*20
            self.hp_bar_sprite.center_y = 790
            self.hp_bar_list.append(self.hp_bar_sprite)

    # удержание камеры по центру игрового поля

    def center_camera_to_player(self):
        self.screen.center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        self.screen.center_y += PERMANENT_SPEED

        if self.screen.center_x != 0:
            self.screen.center_x = 0
        player_centered = self.screen.center_x, self.screen.center_y
        self.camera.move_to(player_centered)

    # Отрисовка

    def on_draw(self):
        """Render the screen."""
        self.clear()
        self.back_list.draw()
        self.camera.use()

        self.scene.draw()
        # Draw sprites
        self.player_list.draw()
        self.bullet_list.draw()
        self.shoot_sprite_list.draw()
        self.bullet_enemy_list.draw()
        self.explosion_list.draw()
        # Gui camera
        self.gui_camera.use()
        self.hp_bar_list.draw()
        arcade.draw_text(
            str(self.score),
            370,
            750,
            arcade.csscolor.WHITE,
            18,
        )

    # Стельба игрока

    def shoot(self, speed, list_sp, bullet_image):
        for block in list_sp:
            if self.key_space_pressed:
                bullet = arcade.Sprite(bullet_image, SPRITE_SCALING_LASER)
                bullet.center_x = block.center_x
                bullet.center_y = block.center_y + speed
                self.bullet_list.append(bullet)

                shoot_sprite = arcade.Sprite("images/shoot.png", SHOOT_SCALING)
                shoot_sprite.center_y = self.player_sprite.center_y + 8
                shoot_sprite.center_x = self.player_sprite.center_x
                self.shoot_sprite_list.append(shoot_sprite)
                #self.shoot_sprite_list.pop()
                self.shoot_numbers.append(0)

    def empty_shoot(self):
        for i in range(1, len(self.shoot_sprite_list) - 1):
            if i >= len(self.shoot_sprite_list):
                break
            self.shoot_numbers[i] += 1
            if self.shoot_numbers[i] >= 5:
                self.shoot_numbers.pop(i)
                self.shoot_sprite_list.pop(i)

    # Стельба противников

    def shoot_enemy(self, speed, list_sp, bullet_image):
        for block in list_sp:
            if 0 <= block.center_y <= self.screen.center_y + SCREEN_HEIGHT \
                    and 0 <= block.center_x <= self.screen.center_x + SCREEN_WIDTH:
                bullet = arcade.Sprite(bullet_image, SPRITE_SCALING_LASER)
                bullet.center_x = block.center_x
                bullet.center_y = block.center_y + speed
                self.bullet_enemy_list.append(bullet)

    # Движение противников

    def enemy_movement(self, list_sl):
        for block in list_sl:
            if block.center_y < self.screen.center_y + SCREEN_HEIGHT - 100:
                block.center_x += 1

    # Удаление снарядов за пределами экрана

    def bulbabeggins(self):
        for bullet in self.bullet_list:
            bullet.center_y += BULLET_SPEED
            if bullet.center_y >= self.screen.center_y + SCREEN_HEIGHT-15:
                self.bullet_list.remove(bullet)
        for bullet in self.bullet_enemy_list:
            bullet.center_y -= BULLET_ENEMY_SPEED
            if bullet.center_y <= 0:
                self.bullet_enemy_list.remove(bullet)

    # Расчёт коллизии для снарядов

    def calculate_collision_for_bullets(self, bullet_list_for_collide, list, flag):
        for bullet in bullet_list_for_collide:
            for block in list:
                left_block_border = int(block.center_x) - int(block.width) / 2
                right_block_border = int(block.center_x) + int(block.width) / 2
                surface_block = int(block.center_y) + int(block.height) / 2
                bottom_block = int(block.center_y) - int(block.height) / 2
                if left_block_border <= bullet.center_x <= right_block_border \
                        and surface_block >= bullet.center_y >= bottom_block:
                    bullet_list_for_collide.remove(bullet)
                    explosion = arcade.Sprite("images/explosion.png", TILE_SCALING)
                    explosion.center_x = block.center_x
                    explosion.center_y = block.center_y
                    self.explosion_list.append(explosion)
                    self.sprite_with_bullet(flag)
                    self.explosion_numbers.append(0)
                    if flag != 0:
                        list.remove(block)
                    break

    #Столкновение спрайтов и пуль

    def sprite_with_bullet(self, flag):
        if flag == 0:
            self.damage += 1
            self.hp_bar_list.pop()
            if self.damage >= HP:
                self.end_the_game()
        if flag == 1:
            self.score += 10
        if flag == 2:
            self.score += 20

    # окончание игры

    def end_the_game(self):
        record = []
        f = open("record.txt", "r+", encoding='utf-8')
        f2 = open("record with no №.txt", "r+", encoding='utf-8')
        f2.write(str(self.score) + "\n")
        for row in f2:
            s = ""
            for i in range(len(row)):
                if row[i].isdigit():
                    s += row[i]
            record.append(int(s))
        record.append(self.score)
        record.sort(reverse=True)
        for i in range(len(record)):
            if i+1 < 10:
                p = " "
            else: p = ""
            s = str(i + 1) + p + "   " + str(record[i]) + "\n"
            f.write(s)
        f.close()
        f2.close()

        exit()

    # Анимация взрыва противников

    def explosion_sprite(self):
        for i in range(1, len(self.explosion_numbers)-1):
            if i >= len(self.explosion_numbers):
                break
            self.explosion_numbers[i] += 1
            if self.explosion_numbers[i] >= 5:
                self.explosion_numbers.pop(i)
                self.explosion_list.pop(i)

    # Движение противников

    def player_movement(self):
        if self.collideup or self.player_sprite.center_y > self.screen.center_y + 770:
            self.player_up = 0
        else:
            self.player_up = PLAYER_UP_SPEED
        if self.collidedown or self.player_sprite.center_y < self.screen.center_y + 15:
            self.player_down = 0
            self.player_sprite.center_y += PERMANENT_SPEED
        else:
            self.player_down = PLAYER_DOWN_SPEED
        if self.collideleft or self.player_sprite.center_x < 15:
            self.player_left = 0
        else:
            self.player_left = PLAYER_LEFT_SPEED
        if self.collideright or self.player_sprite.center_x > 429:
            self.player_right = 0
        else:
            self.player_right = PLAYER_RIGHT_SPEED

        if self.key_right_pressed:
            self.player_sprite.center_x += self.player_right
        if self.key_left_pressed:
            self.player_sprite.center_x -= self.player_left
        if self.key_up_pressed:
            self.player_sprite.center_y += self.player_up
        if self.key_down_pressed:
            self.player_sprite.center_y -= self.player_down

    # Расчёт коллизии игрока с противниками

    def calculate_collision(self):
        self.collideup = False
        self.collidedown = False
        self.collideleft = False
        self.collideright = False
        scale_sprite = TILE_SCALING * 5
        left_player_border = self.player_sprite.center_x - int(self.player_sprite.width) / 2 + scale_sprite
        right_player_border = self.player_sprite.center_x + int(self.player_sprite.width) / 2 - scale_sprite
        surface_player = self.player_sprite.center_y + int(self.player_sprite.height) / 2 - scale_sprite
        bottom_player = self.player_sprite.center_y - int(self.player_sprite.height) / 2 + scale_sprite
        for block in self.scene["guys"]:
            left_block_border = int(block.center_x) - int(block.width) / 2 + scale_sprite
            right_block_border = int(block.center_x) + int(block.width) / 2 - scale_sprite
            surface_block = int(block.center_y) + int(block.height) / 2 - scale_sprite
            bottom_block = int(block.center_y) - int(block.height) / 2 + scale_sprite
            "down collision"
            "collision up"
            if right_player_border >= left_block_border and left_player_border < right_block_border and surface_block > surface_player >= bottom_block:
                self.collideup = True
            if right_player_border >= left_block_border and left_player_border < right_block_border and bottom_player <= surface_block < surface_player:
                self.collidedown = True
            "collision left"
            if left_player_border <= right_block_border < right_player_border and surface_player > bottom_block and bottom_player < surface_block:
                self.collideleft = True
            "collision right"
            if right_block_border > right_player_border >= left_block_border and surface_player > bottom_block and bottom_player < surface_block:
                self.collideright = True

    # Обновление функций

    def on_update(self, delta_time):
        self.center_camera_to_player()
        self.player_movement()
        self.calculate_collision()
        self.bulbabeggins()
        self.shoot_timer_enemy += delta_time
        self.big_shoot_timer += delta_time
        self.shoot_timer_player += delta_time
        if self.shoot_timer_player >= SHOOT_INTERVAL:
            self.shoot(BULLET_SPEED, self.player_list, "images/bullet.png")
            self.shoot_timer_player = 0
        if self.shoot_timer_enemy >= SHOOT_ENEMY_INTERVAL:
            self.shoot_enemy(-BULLET_ENEMY_SPEED, self.scene["guys"], "images/bullet_up_side_down.png")
            self.shoot_timer_enemy = 0
        if self.big_shoot_timer >= SHOOT_ENEMY_INTERVAL/3:
            self.shoot_enemy(-BULLET_ENEMY_SPEED, self.scene["big guys"], "images/bullet_up_side_down.png")
            self.big_shoot_timer = 0
        self.calculate_collision_for_bullets(self.bullet_list, self.scene["guys"], 1)
        self.calculate_collision_for_bullets(self.bullet_list, self.scene["big guys"], 2)
        self.calculate_collision_for_bullets(self.bullet_enemy_list, self.player_list, 0)
        self.explosion_time += delta_time
        if self.explosion_time >= 0.5:
            self.explosion_sprite()
            self.explosion_time = 0
        self.enemy_movement(self.scene["big guys"])
        self.timer += delta_time
        if self.timer >= 0.05:
            self.empty_shoot()
            self.timer = 0



    # Нажатие на клавиши

    def on_key_press(self, key, modifiers):

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.key_up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.key_down_pressed = True
        elif key == arcade.key.SPACE:
            self.key_space_pressed = True

    # Зажатие клавиши

    def on_key_release(self, key, modifiers):

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.key_up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.key_down_pressed = False
        elif key == arcade.key.SPACE:
            self.key_space_pressed = False

# Запуск игры


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
