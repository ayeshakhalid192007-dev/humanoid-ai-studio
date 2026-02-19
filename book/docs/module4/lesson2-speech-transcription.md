---
title: "Lesson 2: Speech Transcription"
sidebar_position: 3
description: "Set up speech-to-text with OpenAI Whisper for robot voice commands."
---

# Lesson 2: Speech-to-Text with Whisper

## Prediction Phase

- How accurate is speech recognition in noisy environments?
- What is the latency difference between local and cloud-based transcription?
- How do you detect when someone starts and stops speaking?

---

## OpenAI Whisper

Whisper is a general-purpose speech recognition model that handles multiple languages, accents, and background noise.

### Setup

```bash
pip install openai sounddevice numpy
```

### Basic Transcription

```python
import openai
from pathlib import Path

client = openai.OpenAI()

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe an audio file using Whisper."""
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            response_format="text"
        )
    return transcript
```

### Real-Time Audio Capture

```python
import sounddevice as sd
import numpy as np
import wave
import tempfile

def record_audio(duration: float = 5.0, sample_rate: int = 16000) -> str:
    """Record audio from microphone and save to temp file."""
    print(f"Recording for {duration}s...")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()  # Wait until recording is finished

    # Save to WAV file
    temp_file = tempfile.mktemp(suffix='.wav')
    with wave.open(temp_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    return temp_file


def voice_command_loop():
    """Continuous voice command capture and transcription."""
    while True:
        input("Press Enter to record a command...")
        audio_file = record_audio(duration=5.0)
        text = transcribe_audio(audio_file)
        print(f"Transcribed: {text}")
        yield text
```

### ROS 2 Integration

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SpeechNode(Node):
    def __init__(self):
        super().__init__('speech_transcriber')
        self.publisher = self.create_publisher(String, '/speech/text', 10)
        self.timer = self.create_timer(0.1, self.check_audio)
        self.get_logger().info('Speech transcriber ready')

    def check_audio(self):
        # In production: use voice activity detection
        # to trigger recording automatically
        pass

    def publish_transcription(self, text: str):
        msg = String()
        msg.data = text
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: {text}')
```

## Handling Noise and Edge Cases

| Issue | Solution |
|-------|----------|
| Background noise | Use noise suppression (noisereduce library) |
| Incomplete commands | Set minimum confidence threshold |
| Domain vocabulary | Use prompt parameter for context |
| Multiple speakers | Ignore, or use speaker diarization |

:::tip Domain-Specific Accuracy
Pass a prompt to Whisper with domain vocabulary to improve accuracy:
```python
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    prompt="Robot commands: navigate, pick up, put down, stop, go to"
)
```
:::

---

## Execution Phase

1. Install dependencies: `pip install openai sounddevice numpy`
2. Test basic transcription with a recorded audio file
3. Implement real-time audio capture
4. Create a ROS 2 node that publishes transcribed text
5. Test with various speaking speeds, volumes, and accents

---

## Reflection

- What was the transcription latency for different audio lengths?
- How did background noise affect accuracy?
- What domain-specific vocabulary improved recognition?
