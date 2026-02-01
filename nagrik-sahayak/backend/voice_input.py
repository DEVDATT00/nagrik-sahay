import speech_recognition as sr

def voice_to_text(language="hi-IN"):
    r = sr.Recognizer()
    
    # 🕒 ADJUST THESE SETTINGS FOR LONG COMPLAINTS 
    r.pause_threshold = 2.5  # Wait 2.5 seconds of silence before stopping (Default is 0.8)
    r.phrase_threshold = 0.3 # Minimum length of a "phrase" to consider
    r.non_speaking_duration = 1.0 # Keep recording for 1s even if no sound is detected
    
    with sr.Microphone() as source:
        print("🎙️ System is listening for your full complaint...")
        print("💡 Tip: You can take short pauses now without the system stopping.")
        
        # Help the AI hear you over background noise 
        r.adjust_for_ambient_noise(source, duration=1.2)
        
        try:
            # Capture the audio
            audio = r.listen(source, timeout=15, phrase_time_limit=45) # Max 45 seconds 
            print("⏳ Processing your voice...")
            
            text = r.recognize_google(audio, language=language)
            print("🗣️ Full Transcript:", text)
            return text
            
        except sr.WaitTimeoutError:
            return "Error: No speech detected (Timeout)"
        except sr.UnknownValueError:
            return "Voice not understood"
        except sr.RequestError:
            return "Speech service not available"