import { PollyClient, SynthesizeSpeechCommand } from '@aws-sdk/client-polly';

class PollyService {
  constructor() {
    this.currentAudio = null;
    this.backendUrl = process.env.REACT_APP_API_URL || 'http://44.203.95.38:8000';
  }

  /**
   * Synthesize speech and return audio data URL (for manual playback control)
   * This is used for lip-sync integration
   */
  async synthesize(text, voiceId = 'Joanna') {
    try {
      console.log('🔊 [Polly] Synthesizing:', text.substring(0, 50) + '...');

      // Call backend API
      const response = await fetch(`${this.backendUrl}/api/polly/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voiceId: voiceId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to synthesize speech');
      }

      // Convert base64 to audio data URL
      const audioDataURL = this.base64ToDataURL(data.audio);
      console.log('✅ [Polly] Audio synthesized successfully');
      
      return audioDataURL;
    } catch (error) {
      console.error('❌ [Polly] Synthesis error:', error);
      throw error;
    }
  }

  /**
   * Original speak method - synthesize and play immediately
   */
  async speak(text, voiceId = 'Joanna') {
    try {
      // Stop any currently playing audio
      this.stop();

      console.log('🔊 Requesting speech synthesis...', text.substring(0, 50));

      // Call backend API
      const response = await fetch(`${this.backendUrl}/api/polly/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voiceId: voiceId
        })
      });

      const data = await response.json();
      console.log('🔊 Backend response:', { success: data.success, audioLength: data.audio?.length });

      if (!data.success) {
        throw new Error(data.error || 'Failed to synthesize speech');
      }

      // Convert base64 audio to blob
      const audioBlob = this.base64ToBlob(data.audio, 'audio/mpeg');
      const audioUrl = URL.createObjectURL(audioBlob);

      console.log('🔊 Audio blob created, size:', audioBlob.size, 'bytes');

      // Create and play audio
      this.currentAudio = new Audio(audioUrl);

      return new Promise((resolve, reject) => {
        this.currentAudio.onloadeddata = () => {
          console.log('🔊 Audio loaded, duration:', this.currentAudio.duration);
        };

        this.currentAudio.onplay = () => {
          console.log('🔊 Audio playing...');
        };

        this.currentAudio.onended = () => {
          console.log('🔊 Audio finished');
          URL.revokeObjectURL(audioUrl);
          this.currentAudio = null;
          resolve();
        };

        this.currentAudio.onerror = (error) => {
          console.error('🔊 Audio playback error:', error);
          URL.revokeObjectURL(audioUrl);
          this.currentAudio = null;
          reject(error);
        };

        // Start playback
        this.currentAudio.play()
          .then(() => console.log('🔊 Play() called successfully'))
          .catch((err) => {
            console.error('🔊 Play() failed:', err);
            reject(err);
          });
      });
    } catch (error) {
      console.error('🔊 Polly error:', error);
      throw error;
    }
  }

  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
      console.log('🔊 Audio stopped');
    }
  }

  isPlaying() {
    return this.currentAudio && !this.currentAudio.paused;
  }

  /**
   * Convert base64 to data URL (for Audio element)
   */
  base64ToDataURL(base64) {
    return `data:audio/mpeg;base64,${base64}`;
  }

  /**
   * Convert base64 to Blob (for object URL)
   */
  base64ToBlob(base64, mimeType) {
    try {
      const byteCharacters = atob(base64);
      const byteNumbers = new Array(byteCharacters.length);

      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      return new Blob([byteArray], { type: mimeType });
    } catch (error) {
      console.error('🔊 Base64 decode error:', error);
      throw error;
    }
  }
}

export const pollyService = new PollyService();
