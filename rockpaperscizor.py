import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import random
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont

from mutagen import File
from io import BytesIO
import base64

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPS Game + Music Player")
        self.root.geometry("400x600")  # Increased height for metadata
        self.root.resizable(False, False)
        
        pygame.mixer.init()
        
        self.setup_game()
        self.setup_music_player()
        
    def setup_game(self):
        game_frame = ttk.LabelFrame(self.root, text="Rock Paper Scissors", padding=5)
        game_frame.pack(fill="x", padx=5, pady=5)
        
        # Score
        self.score_label = ttk.Label(game_frame, text="Score: 0 - 0")
        self.score_label.pack()
        
        # Game buttons
        btn_frame = ttk.Frame(game_frame)
        btn_frame.pack(pady=5)
        
        for choice in ['Rock', 'Paper', 'Scissors']:
            ttk.Button(btn_frame, text=choice, 
                      command=lambda c=choice: self.play(c)).pack(side='left', padx=2)
        
        self.result_label = ttk.Label(game_frame, text="Choose your move!")
        self.result_label.pack()
        
        self.user_score = 0
        self.comp_score = 0
        
    def setup_music_player(self):
        music_frame = ttk.LabelFrame(self.root, text="Music Player", padding=5)
        music_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Album art display
        self.art_size = (150, 150)
        self.art_label = ttk.Label(music_frame)
        self.art_label.pack(pady=5)
        
        # Metadata display
        self.metadata_frame = ttk.Frame(music_frame)
        self.metadata_frame.pack(fill='x', pady=5)
        
        self.title_label = ttk.Label(self.metadata_frame, text="Title: -")
        self.title_label.pack()
        
        self.artist_label = ttk.Label(self.metadata_frame, text="Artist: -")
        self.artist_label.pack()
        
        self.album_label = ttk.Label(self.metadata_frame, text="Album: -")
        self.album_label.pack()
        
        # Set default icon
        self.set_default_icon()
        
        # Music controls
        ctrl_frame = ttk.Frame(music_frame)
        ctrl_frame.pack(fill='x', pady=5)
        
        ttk.Button(ctrl_frame, text="🎵", width=3,
                  command=self.add_music).pack(side='left', padx=2)
        
        self.play_btn = ttk.Button(ctrl_frame, text="▶", width=3,
                                 command=self.toggle_play)
        self.play_btn.pack(side='left', padx=2)
        
        ttk.Button(ctrl_frame, text="⏹", width=3,
                  command=self.stop_music).pack(side='left', padx=2)
        
        # Volume
        self.volume = tk.DoubleVar(value=0.5)
        ttk.Scale(ctrl_frame, from_=0, to=1, variable=self.volume,
                 command=lambda v: pygame.mixer.music.set_volume(float(v)),
                 orient='horizontal').pack(side='right', fill='x', expand=True, padx=5)
        
        # Playlist
        self.playlist = tk.Listbox(music_frame, height=8)
        self.playlist.pack(fill='both', expand=True, pady=5)
        self.playlist.bind('<<ListboxSelect>>', self.on_select_song)
        
        self.is_playing = False
        self.music_files = []
        self.metadata_cache = {}
        
    def set_default_icon(self):
        # Create a default music icon
        img = Image.new('RGB', self.art_size, 'lightgray')
        draw = ImageDraw.Draw(img)
        draw.text((75, 75), '♪', fill='white', anchor='mm', font=ImageFont.truetype("arial.ttf", 50))
        photo = ImageTk.PhotoImage(img)
        self.art_label.configure(image=photo)
        self.art_label.image = photo
        
    def extract_metadata(self, file_path):
        if file_path in self.metadata_cache:
            return self.metadata_cache[file_path]
            
        metadata = {
            'title': os.path.basename(file_path),
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'artwork': None
        }
        
        try:
            audio = File(file_path)
            if audio is not None:
                if hasattr(audio, 'tags'):
                    tags = audio.tags
                    if 'title' in tags:
                        metadata['title'] = tags['title'][0]
                    if 'artist' in tags:
                        metadata['artist'] = tags['artist'][0]
                    if 'album' in tags:
                        metadata['album'] = tags['album'][0]
                    
                    # Try to extract artwork
                    if 'APIC:' in tags:
                        artwork = tags['APIC:'].data
                        img = Image.open(BytesIO(artwork))
                        img = img.resize(self.art_size, Image.Resampling.LANCZOS)
                        metadata['artwork'] = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            
        self.metadata_cache[file_path] = metadata
        return metadata
        
    def update_display(self, metadata):
        self.title_label['text'] = f"Title: {metadata['title']}"
        self.artist_label['text'] = f"Artist: {metadata['artist']}"
        self.album_label['text'] = f"Album: {metadata['album']}"
        
        if metadata['artwork']:
            self.art_label.configure(image=metadata['artwork'])
            self.art_label.image = metadata['artwork']
        else:
            self.set_default_icon()
            
    def on_select_song(self, event):
        selection = self.playlist.curselection()
        if selection:
            file_path = self.music_files[selection[0]]
            metadata = self.extract_metadata(file_path)
            self.update_display(metadata)
        
    def play(self, user_choice):
        choices = ['Rock', 'Paper', 'Scissors']
        comp_choice = random.choice(choices)
        
        if user_choice == comp_choice:
            result = "Tie!"
        elif ((user_choice == 'Rock' and comp_choice == 'Scissors') or
              (user_choice == 'Paper' and comp_choice == 'Rock') or
              (user_choice == 'Scissors' and comp_choice == 'Paper')):
            result = "You win!"
            self.user_score += 1
        else:
            result = "Computer wins!"
            self.comp_score += 1
            
        self.score_label['text'] = f"Score: {self.user_score} - {self.comp_score}"
        self.result_label['text'] = f"{result}\nYou: {user_choice} vs PC: {comp_choice}"
        
    def add_music(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio Files", "*.mp3 *.wav")])
        
        for file in files:
            self.music_files.append(file)
            self.playlist.insert(tk.END, os.path.basename(file))
            
        # If this is the first song added, select it
        if len(self.music_files) == len(files):
            self.playlist.selection_set(0)
            self.on_select_song(None)
            
    def toggle_play(self):
        if not self.music_files:
            return
            
        selected = self.playlist.curselection()
        if not selected:
            self.playlist.selection_set(0)
            selected = (0,)
            
        if not self.is_playing:
            try:
                pygame.mixer.music.load(self.music_files[selected[0]])
                pygame.mixer.music.play()
                self.play_btn['text'] = "⏸"
                
                # Update metadata display
                metadata = self.extract_metadata(self.music_files[selected[0]])
                self.update_display(metadata)
            except pygame.error:
                return
        else:
            pygame.mixer.music.pause()
            self.play_btn['text'] = "▶"
            
        self.is_playing = not self.is_playing
        
    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn['text'] = "▶"

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()