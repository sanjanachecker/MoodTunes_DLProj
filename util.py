from midi2audio import FluidSynth
import pretty_midi
import numpy as np
import matplotlib.pyplot as plt

TIME_STEP = 0.001
MAX_TIME = 30.0

def midi_to_audio(midi_file_path, audio_file_path, sound_font_path="FluidR3_GM.sf2"):
  fs = FluidSynth(sound_font_path)
  fs.midi_to_audio(midi_file_path, audio_file_path)
  print(f"Conversion complete: {audio_file_path}")

def midi_to_vector(file_path, time_step=TIME_STEP, max_time=MAX_TIME):
  # Load MIDI file
  midi_data = pretty_midi.PrettyMIDI(file_path)

  # Create a time grid from 0 to max_time with intervals of time_step
  time_grid = np.arange(0, max_time, time_step)
  # Initialize arrays for notes, velocities, and duration
  note_matrix = np.zeros((len(time_grid), 128))  # 128 possible MIDI pitches

  print(midi_data.instruments)

  for instrument in midi_data.instruments:
    if instrument.is_drum: continue

    for note in instrument.notes:
      # Find the closest time step to the note start and end
      start_idx = int(note.start // time_step)
      end_idx = int(note.end // time_step)

      if (note.start > max_time): continue

      # Limit indices to the length of time grid
      start_idx = min(start_idx, len(time_grid) - 1)
      end_idx = min(end_idx, len(time_grid) - 1)

      note_matrix[start_idx:end_idx, note.pitch] = note.velocity

  return note_matrix

def vector_to_midi(vector, time_step=TIME_STEP, max_time=MAX_TIME):
  num_pitches = 128
  num_time_steps = int(max_time / time_step)
  note_matrix = vector.reshape((num_time_steps, num_pitches))
  
  # Create a PrettyMIDI object
  midi_data = pretty_midi.PrettyMIDI()
  instrument = pretty_midi.Instrument(program=0)  # Default to a piano instrument

  for pitch in range(num_pitches):
    active_time_steps = np.where(note_matrix[:, pitch] > 0)[0]
    
    if len(active_time_steps) == 0: continue

    start_idx = active_time_steps[0]
    for i in range(1, len(active_time_steps)):
      if active_time_steps[i] != active_time_steps[i - 1] + 1:
        start_time = start_idx * time_step
        end_time = active_time_steps[i - 1] * time_step
        velocity = int(note_matrix[start_idx, pitch])
        note = pretty_midi.Note(velocity=velocity,pitch=pitch,start=start_time,end=end_time)
        instrument.notes.append(note)
        start_idx = active_time_steps[i]
    
    start_time = start_idx * time_step
    end_time = active_time_steps[-1] * time_step
    velocity = int(note_matrix[start_idx, pitch])
    note = pretty_midi.Note(velocity=velocity,pitch=pitch,start=start_time,end=end_time)
    instrument.notes.append(note)

  midi_data.instruments.append(instrument)
  return midi_data


vec = midi_to_vector('example.mid')
midi = vector_to_midi(vec.flatten())
midi.write("output_file.mid")


plt.imshow(vec * 2, cmap='plasma')
plt.show()

midi_to_audio('output_file.mid', 'new.wav')
