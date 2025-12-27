import wave
import math
import struct
import random
import os

def generate_wav(filename, duration, frequency, volume=0.5, wave_type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'sine':
                value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
            elif wave_type == 'square':
                value = int(volume * 32767.0 * (1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0))
            elif wave_type == 'sawtooth':
                value = int(volume * 32767.0 * (2.0 * (t * frequency - math.floor(t * frequency + 0.5))))
            elif wave_type == 'noise':
                value = int(volume * 32767.0 * (random.random() * 2 - 1))
            
            wav_file.writeframes(struct.pack('<h', value))

def generate_sounds():
    print("Generating sounds...")
    

    

    generate_wav('chomp.wav', 0.1, 300, 0.3, 'square')
    

    generate_wav('eat_ghost.wav', 0.2, 800, 0.4, 'sawtooth')
    

    generate_wav('death.wav', 0.5, 100, 0.5, 'noise')
   
    generate_wav('win.wav', 1.0, 600, 0.4, 'sine')
    
 
    generate_wav('powerup.wav', 0.3, 1000, 0.3, 'sine')
    
    print("Sounds generated successfully!")

if __name__ == "__main__":
    generate_sounds()

