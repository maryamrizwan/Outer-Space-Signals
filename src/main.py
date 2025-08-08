#!/usr/bin/env python3
import re 
from collections import Counter
import string
import nltk       
from nltk.corpus import words

"""Process Explained:
PROCESS: 
I used a window of size 721 over the whole text. Which means 64815 windows were created. After every 1 alphabet,
a new window is started. The goal was to find the best window which gives us the most english like words after
decrypting using the 10 top-most used english letters given. I have selected the window after decrypting 
every window (using most letters used in that window and substituting in english), and then using nltk 
library to see which has the most english-like letters. Since, we don't have all 26 substitutions and only 10 were
transformed for each window, I did not get a whole english sentence in any window. But I used the window which could get us the closest to
english-like words. 
"""

class SignalDecoder:
    def __init__(self, signal_file, length_of_window):
        self.signal_file = signal_file
        self.message_length = length_of_window
        self.english_freq = ['E', 'A', 'T', 'O', 'I', 'R', 'S', 'N', 'H', 'U']
        
        nltk.data.find('corpora/words')      
        self.english_words = set(word.upper() for word in words.words())
        self.use_nltk = True 

    def load_signal(self):   #read file
        with open(self.signal_file, 'r') as f:
            return f.read().strip()
    
    def get_sliding_windows(self, signal):
        windows = []
        signal_length = len(signal)
        for i in range(signal_length - self.message_length + 1): #how many windows will be formed
            window = signal[i:i + self.message_length]  #picking 721 letters from each window
            windows.append((i, window))
        
        print(f"Generated {len(windows)} sliding windows")
        return windows
    
    def analyze_frequency(self, text):    #getting top 10 letters in each window
        letters_only = ''.join(c for c in text if c.isupper())
        freq_counter = Counter(letters_only)
        
        top_letters = [letter for letter, count in freq_counter.most_common(10)]
        return top_letters
    
    def create_substitution_map(self, cipher_freq):   #finding substitutions top 10 letters from each window to english letters
        substitution = {}
        
        for i in range(min(len(cipher_freq), len(self.english_freq))):
            substitution[cipher_freq[i]] = self.english_freq[i]
        
        for letter in string.ascii_uppercase:
            if letter not in substitution:
                substitution[letter] = letter
                
        return substitution
    
    def apply_substitution(self, text, substitution):  #substituting letters in each window, leaving the rest as they are
        decoded = ""
        for char in text:
            if char in substitution:
                decoded += substitution[char]
            else:
                decoded += char  
        return decoded
    
    def calculate_word_score(self, text): #comparing the decoded text in each window to the nltk english data to assign a score
        words_in_text = re.findall(r'[A-Z]+', text.upper())
        valid_words = 0
        total_words = len(words_in_text)
        
        for word in words_in_text:
            if word in self.english_words:
                valid_words += 1
        
        if total_words == 0:
            return 0
        
        return (valid_words / total_words) * 100
    
    def decode_signal(self):   
        signal = self.load_signal()
        
        print(f"Signal loaded: {len(signal)} characters")
        windows = self.get_sliding_windows(signal)
        
        best_score = 0
        best_window = None
        best_decoded = None
        best_position = 0
        
        print("Analyzing windows for alien message")
        
        for position, window in windows:          #calling all the functions
            cipher_freq = self.analyze_frequency(window)
            substitution = self.create_substitution_map(cipher_freq) 
            decoded_text = self.apply_substitution(window, substitution)
            score = self.calculate_word_score(decoded_text)
            
            if score > best_score:               #finding the best score out of all the windows
                best_score = score
                best_window = window
                best_decoded = decoded_text
                best_position = position
        
        print(f"\n Best match found at position {best_position}")        
        print(f" Confidence score: {best_score:.2f}% valid English words")
        print(f" Substitution mapping used:")
        
        best_cipher_freq = self.analyze_frequency(best_window)
        best_substitution = self.create_substitution_map(best_cipher_freq)
        
        for cipher, english in best_substitution.items():         #getting all the information from the best window
            if cipher in best_cipher_freq[:10]:  
                print(f"   {cipher} → {english}")
        
        print(f"\n")
        print("DECODED MESSAGE:")
        print("=" * 80)
        print(best_decoded)
        print("=" * 80)
        
        words_list = re.findall(r'[A-Z]+', best_decoded)
        first_9_words = words_list[:9] if len(words_list) >= 9 else words_list
        
        print(f"\n")
        print("First 9 words for submission:")
        print(" ".join(first_9_words))
        
        return {
            'decoded_message': best_decoded,
            'first_9_words': first_9_words,
            'position': best_position,
            'confidence': best_score,
            'substitution': best_substitution
        }

def main():
    decoder = SignalDecoder('signal.txt', 721)
    result = decoder.decode_signal()
    print(f"Message found at position {result['position']} with {result['confidence']:.2f}% confidence")


if __name__ == "__main__":
    main()


