#!/usr/bin/env python3
"""
AI Farming Advisor Backend
A multilingual voice-enabled farming advisory system using AI
"""

import os
import sys
import json
import tempfile
import requests
# Optional audio/punctuation deps: make import resilient for API-only mode
try:
    import speech_recognition as sr  # type: ignore
except Exception:
    sr = None  # type: ignore
try:
    from gtts import gTTS  # type: ignore
except Exception:
    gTTS = None  # type: ignore
try:
    from playsound import playsound  # type: ignore
except Exception:
    playsound = None  # type: ignore
try:
    from deepmultilingualpunctuation import PunctuationModel  # type: ignore
except Exception:
    PunctuationModel = None  # type: ignore
from dotenv import load_dotenv
import time
import re
import platform
import subprocess
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class APIError(Exception):
    """Raised when API operations fail"""
    pass


class AudioError(Exception):
    """Raised when audio operations fail"""
    pass


class FarmingAdvisor:
    """Main AI Farming Advisor application class"""
    
    # Class constants
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL = "llama-3.1-8b-instant"
    DEFAULT_TIMEOUT = 30
    AUDIO_TIMEOUT = 8
    PHRASE_TIME_LIMIT = 15
    
    def __init__(self):
        """Initialize the Farming Advisor with all necessary configurations"""
        self._setup_logging()
        self._load_environment()
        self._initialize_audio_components()
        self._setup_language_configurations()
        self._initialize_app_state()
        
    def _setup_logging(self) -> None:
        """Configure logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('farming_advisor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_environment(self) -> None:
        """Load and validate environment variables"""
        load_dotenv()
        
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            api_mode = os.getenv('API_MODE', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
            if api_mode:
                warn_msg = (
                    "⚠️ GROQ_API_KEY not found. Running in API_MODE with fallback data.\n"
                    "Set GROQ_API_KEY in .env to enable live AI responses."
                )
                print(warn_msg)
                self.logger.warning("GROQ_API_KEY missing; continuing with fallback responses in API_MODE")
                self.groq_api_key = ''
            else:
                error_msg = (
                    "❌ Error: GROQ_API_KEY not found in environment variables.\n"
                    "Please create a .env file with: GROQ_API_KEY=your_api_key_here"
                )
                print(error_msg)
                self.logger.error("Missing GROQ_API_KEY")
                raise ConfigurationError("GROQ_API_KEY is required")
            
    def _initialize_audio_components(self) -> None:
        """Initialize speech recognition and audio processing components"""
        # Allow disabling audio stack in API mode to simplify server runtime
        api_mode = os.getenv('API_MODE', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
        if api_mode:
            self.recognizer = None
            self.microphone = None
            self.punctuation_model = None
            self.logger.info("API_MODE enabled: Skipping audio initialization")
            return

        try:
            if sr is None or PunctuationModel is None:
                raise RuntimeError("Audio libraries not available")
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.punctuation_model = PunctuationModel()
            
            # Configure recognizer for optimal performance
            self._configure_recognizer()
            self._calibrate_microphone()
            
        except Exception as e:
            # Do not crash the API server if audio cannot initialize
            self.logger.warning(f"Audio components not initialized: {e}")
            self.recognizer = None
            self.microphone = None
            self.punctuation_model = None
            
    def _configure_recognizer(self) -> None:
        """Configure speech recognizer with optimal settings"""
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
    def _calibrate_microphone(self) -> None:
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone for ambient noise...")
        try:
            with self.microphone as source:
                self.microphone.CHUNK = 1024
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
            print("✅ Microphone calibrated successfully!")
            self.logger.info("Microphone calibration completed")
        except Exception as e:
            print(f"⚠️ Microphone calibration failed: {e}")
            self.logger.warning(f"Microphone calibration failed: {e}")
            
    def _setup_language_configurations(self) -> None:
        """Setup comprehensive language configurations"""
        self.languages = {
            'en': {
                'name': 'English',
                'code': 'en-US',
                'tts': 'en',
                'prompts': {
                    'crop': "What crop are you planning to plant?",
                    'soil': "What is your soil type? For example: clay, sandy, loamy, or mixed soil.",
                    'location': "What is your location? Please mention your district and state.",
                    'history': "What is your agricultural land crop history? What crops have you grown before?",
                    'followup': "Do you have any follow-up questions about the recommendations? Say 'no' or 'exit' to finish.",
                    'thank_you': "Thank you for using AI Farming Advisor! Have a great harvest!",
                    'recommendations': "Here are your personalized farming recommendations.",
                    'language_selected': "Language selected. Let's start collecting your farming information.",
                    'processing': "Processing your information with AI...",
                    'listening': "Listening... Please speak now",
                    'error_speech': "Could not understand. Please try again.",
                    'error_timeout': "No speech detected. Please try again."
                }
            },
            'hi': {
                'name': 'हिंदी',
                'code': 'hi-IN',
                'tts': 'hi',
                'prompts': {
                    'crop': "आप कौन सी फसल लगाने की योजना बना रहे हैं?",
                    'soil': "आपकी मिट्टी का प्रकार क्या है? उदाहरण: चिकनी मिट्टी, रेतीली मिट्टी, दोमट मिट्टी, या मिश्रित मिट्टी।",
                    'location': "आपका स्थान कहाँ है? कृपया अपने जिले और राज्य का नाम बताएं।",
                    'history': "आपकी कृषि भूमि की फसल का इतिहास क्या है? आपने पहले कौन सी फसलें उगाई हैं?",
                    'followup': "क्या आपके पास सिफारिशों के बारे में कोई और प्रश्न हैं? समाप्त करने के लिए 'नहीं' या 'बाहर निकलें' कहें।",
                    'thank_you': "एआई फार्मिंग सलाहकार का उपयोग करने के लिए धन्यवाद! अच्छी फसल हो!",
                    'recommendations': "यहाँ आपकी व्यक्तिगत कृषि सिफारिशें हैं।",
                    'language_selected': "भाषा चुनी गई। आइए आपकी कृषि जानकारी एकत्र करना शुरू करते हैं।",
                    'processing': "एआई के साथ आपकी जानकारी का विश्लेषण कर रहे हैं...",
                    'listening': "सुन रहे हैं... कृपया अब बोलें",
                    'error_speech': "समझ नहीं आया। कृपया फिर कोशिश करें।",
                    'error_timeout': "आवाज़ नहीं सुनी। कृपया फिर कोशिश करें।"
                }
            },
            'te': {
                'name': 'తెలుగు',
                'code': 'te-IN',
                'tts': 'te',
                'prompts': {
                    'crop': "మీరు ఏ పంట నాటాలని అనుకుంటున్నారు?",
                    'soil': "మీ మట్టి రకం ఏమిటి? ఉదాహరణకు: బంకమట్టి, ఇసుకమట్టి, మిశ్రమ మట్టి లేదా లోమమట్టి।",
                    'location': "మీ ప్రాంతం ఎక్కడ ఉంది? దయచేసి మీ జిల్లా మరియు రాష్ట్రం చెప్పండి।",
                    'history': "మీ వ్యవసాయ భూమి పంట చరిత్ర ఏమిటి? మీరు ఇంతకు మునుపు ఏ పంటలు పండించారు?",
                    'followup': "సిఫార్సుల గురించి మీకు ఏదైనా అనుబంధ ప్రశ్నలు ఉన్నాయా? ముగించడానికి 'లేదు' లేదా 'నిష్క్రమించు' అని చెప్పండి।",
                    'thank_you': "AI వ్యవసాయ సలహాదారుని ఉపయోగించినందుకు ధన్యవాదాలు! మంచి పంట ఉండాలని కోరుకుంటున్నాను!",
                    'recommendations': "ఇవి మీ వ్యక్తిగత వ్యవసాయ సిఫార్సులు.",
                    'language_selected': "భాష ఎంచుకోబడింది. మీ వ్యవసాయ సమాచారాన్ని సేకరించడం ప్రారంభిద్దాం।",
                    'processing': "AI తో మీ సమాచారాన్ని విశ్లేషిస్తున్నాము...",
                    'listening': "వింటున్నాము... దయచేసి ఇప్పుడు మాట్లాడండి",
                    'error_speech': "అర్థం కాలేదు. దయచేసి మళ్లీ ప్రయత్నించండి.",
                    'error_timeout': "మాట వినపడలేదు. దయచేసి మళ్లీ ప్రయత్నించండి."
                }
            },
            'ta': {
                'name': 'தமிழ்',
                'code': 'ta-IN',
                'tts': 'ta',
                'prompts': {
                    'crop': "நீங்கள் என்ன பயிரை நடவு செய்ய திட்டமிட்டுள்ளீர்கள்?",
                    'soil': "உங்கள் மண் வகை என்ன? உதாரணம்: களிமண், மணல், களிமண் கலந்த மண், அல்லது கலப்பு மண்.",
                    'location': "உங்கள் இடம் எங்கே? தயவுசெய்து உங்கள் மாவட்டம் மற்றும் மாநிலத்தைக் குறிப்பிடுங்கள்.",
                    'history': "உங்கள் விவசாய நிலத்தின் பயிர் வரலாறு என்ன? நீங்கள் முன்பு என்ன பயிர்களை வளர்த்தீர்கள்?",
                    'followup': "பரிந்துரைகள் பற்றி உங்களுக்கு ஏதேனும் கூடுதல் கேள்விகள் உள்ளனவா? முடிக்க 'இல்லை' அல்லது 'வெளியேறு' என்று சொல்லுங்கள்.",
                    'thank_you': "AI விவசாய ஆலோசகரைப் பயன்படுத்தியதற்கு நன்றி! நல்ல அறுவடை இருக்கட்டும்!",
                    'recommendations': "இவை உங்கள் தனிப்பட்ட விவசாய பரிந்துரைகள்.",
                    'language_selected': "மொழி தேர்ந்தெடுக்கப்பட்டது. உங்கள் விவசாய தகவல்களை சேகரிக்கத் தொடங்குவோம்.",
                    'processing': "AI மூலம் உங்கள் தகவல்களை பகுப்பாய்வு செய்கிறோம்...",
                    'listening': "கேட்டுக்கொண்டிருக்கிறோம்... தயவுசெய்து இப்போது பேசுங்கள்",
                    'error_speech': "புரியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
                    'error_timeout': "குரல் கேட்கவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
                }
            },
            'kn': {
                'name': 'ಕನ್ನಡ',
                'code': 'kn-IN',
                'tts': 'kn',
                'prompts': {
                    'crop': "ನೀವು ಯಾವ ಬೆಳೆಯನ್ನು ನೆಡಲು ಯೋಜಿಸುತ್ತಿದ್ದೀರಿ?",
                    'soil': "ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರ ಏನು? ಉದಾಹರಣೆ: ಜೇಡಿಮಣ್ಣು, ಮರಳು, ಮಿಶ್ರ ಮಣ್ಣು, ಅಥವಾ ಲೋಮ್ ಮಣ್ಣು।",
                    'location': "ನಿಮ್ಮ ಸ್ಥಳ ಎಲ್ಲಿದೆ? ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಮತ್ತು ರಾಜ್ಯವನ್ನು ತಿಳಿಸಿ।",
                    'history': "ನಿಮ್ಮ ಕೃಷಿ ಭೂಮಿಯ ಬೆಳೆ ಇತಿಹಾಸ ಏನು? ನೀವು ಮೊದಲು ಯಾವ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಸಿದ್ದೀರಿ?",
                    'followup': "ಶಿಫಾರಸುಗಳ ಬಗ್ಗೆ ನಿಮಗೆ ಯಾವುದೇ ಮುಂದಿನ ಪ್ರಶ್ನೆಗಳಿವೆಯೇ? ಮುಗಿಸಲು 'ಇಲ್ಲ' ಅಥವಾ 'ನಿರ್ಗಮಿಸು' ಎಂದು ಹೇಳಿ।",
                    'thank_you': "AI ಕೃಷಿ ಸಲಹೆಗಾರನನ್ನು ಬಳಸಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದ! ಉತ್ತಮ ಸುಗ್ಗಿಯಾಗಲಿ!",
                    'recommendations': "ಇವು ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಕೃಷಿ ಶಿಫಾರಸುಗಳು.",
                    'language_selected': "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ. ನಿಮ್ಮ ಕೃಷಿ ಮಾಹಿತಿಯನ್ನು ಸಂಗ್ರಹಿಸಲು ಪ್ರಾರಂಭಿಸೋಣ.",
                    'processing': "AI ನೊಂದಿಗೆ ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದ್ದೇವೆ...",
                    'listening': "ಕೇಳುತ್ತಿದ್ದೇವೆ... ದಯವಿಟ್ಟು ಈಗ ಮಾತನಾಡಿ",
                    'error_speech': "ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
                    'error_timeout': "ಧ್ವನಿ ಕೇಳಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
                }
            },
            'or': {
                'name': 'ଓଡ଼ିଆ',
                'code': 'or-IN',
                'tts': 'or',
                'prompts': {
                    'crop': "ଆପଣ କେଉଁ ଫସଲ ରୋପଣ କରିବାକୁ ଯୋଜନା କରୁଛନ୍ତି?",
                    'soil': "ଆପଣଙ୍କର ମାଟି ପ୍ରକାର କ'ଣ? ଉଦାହରଣ: ମାଟି, ବାଲି, ଲୋମ, କିମ୍ବା ମିଶ୍ରିତ ମାଟି।",
                    'location': "ଆପଣଙ୍କର ସ୍ଥାନ କେଉଁଠି? ଦୟାକରି ଆପଣଙ୍କର ଜିଲ୍ଲା ଏବଂ ରାଜ୍ୟ ଉଲ୍ଲେଖ କରନ୍ତୁ।",
                    'history': "ଆପଣଙ୍କର କୃଷି ଜମିର ଫସଲ ଇତିହାସ କ'ଣ? ଆପଣ ପୂର୍ବରୁ କେଉଁ ଫସଲ ବୃଦ୍ଧି କରିଛନ୍ତି?",
                    'followup': "ସୁପାରିଶ ବିଷୟରେ ଆପଣଙ୍କର କୌଣସି ଅନୁସରଣ ପ୍ରଶ୍ନ ଅଛି କି? ସମାପ୍ତ କରିବାକୁ 'ନାହିଁ' କିମ୍ବା 'ବାହାର' କୁହନ୍ତୁ।",
                    'thank_you': "AI କୃଷି ପରାମର୍ଶଦାତା ବ୍ୟବହାର କରିଥିବାରୁ ଧନ୍ୟବାଦ! ଭଲ ଅମଳ ହେଉ!",
                    'recommendations': "ଏଗୁଡ଼ିକ ହେଉଛି ଆପଣଙ୍କର ବ୍ୟକ୍ତିଗତ କୃଷି ସୁପାରିଶ।",
                    'language_selected': "ଭାଷା ଚୟନ ହୋଇଛି। ଆସନ୍ତୁ ଆପଣଙ୍କର କୃଷି ସୂଚନା ସଂଗ୍ରହ କରିବା ଆରମ୍ଭ କରିବା।",
                    'processing': "AI ସହିତ ଆପଣଙ୍କର ସୂଚନା ବିଶ୍ଳେଷଣ କରୁଛୁ...",
                    'listening': "ଶୁଣୁଛୁ... ଦୟାକରି ଏବେ କୁହନ୍ତୁ",
                    'error_speech': "ବୁଝି ପାରିଲି ନାହିଁ। ଦୟାକରି ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।",
                    'error_timeout': "ଆବାଜ ଶୁଣାଗଲା ନାହିଁ। ଦୟାକରି ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।"
                }
            }
        }
        
    def _initialize_app_state(self) -> None:
        """Initialize application state variables"""
        self.selected_language: Optional[str] = None
        self.farmer_data: Dict[str, str] = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Exit words for different languages
        self.exit_words = {
            'en': ['no', 'exit', 'quit', 'bye', 'goodbye', 'stop'],
            'hi': ['नहीं', 'बाहर', 'समाप्त', 'अलविदा', 'रुको'],
            'te': ['లేదు', 'నిష్క్రమించు', 'ముగించు', 'బాయ్', 'ఆపు'],
            'ta': ['இல்லை', 'வெளியேறு', 'முடி', 'பை', 'நிறுத்து'],
            'kn': ['ಇಲ್ಲ', 'ನಿರ್ಗಮಿಸು', 'ಮುಗಿಸು', 'ಬೈ', 'ನಿಲ್ಲಿಸು'],
            'or': ['ନାହିଁ', 'ବାହାର', 'ସମାପ୍ତ', 'ବାଇ', 'ବନ୍ଦ']
        }
        
    def select_language(self) -> None:
        """Allow user to select preferred language with enhanced interface"""
        print("\n" + "="*60)
        print("🌾 Welcome to AI Farming Advisor! 🌾")
        print("="*60)
        
        # Multilingual welcome message
        welcome_messages = [
            "Please select your preferred language:",
            "कृपया अपनी पसंदीदा भाषा चुनें:",
            "దయచేసి మీ ఇష్టమైన భాషను ఎంచుకోండి:",
            "தயவுசெய்து உங்கள் விருப்பமான மொழியைத் தேர்ந்தெடுக்கவும்:",
            "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ:",
            "ଦୟାକରି ଆପଣଙ୍କର ପସନ୍ଦର ଭାଷା ଚୟନ କରନ୍ତୁ:"
        ]
        
        for msg in welcome_messages:
            print(msg)
        
        print("\n📋 Available Languages:")
        print("-" * 30)
        for code, lang_info in self.languages.items():
            print(f"  {code.upper()}: {lang_info['name']}")
        
        while True:
            try:
                choice = input(f"\n🎯 Enter language code ({'/'.join(self.languages.keys())}): ").lower().strip()
                
                if choice in self.languages:
                    self.selected_language = choice
                    lang_name = self.languages[choice]['name']
                    print(f"✅ Language selected: {lang_name}")
                    
                    # Log language selection
                    self.logger.info(f"Language selected: {lang_name} ({choice})")
                    
                    # Provide confirmation in selected language
                    confirmation_msg = self.languages[choice]['prompts']['language_selected']
                    self.text_to_speech(confirmation_msg)
                    return
                    
                elif choice in ['help', 'h', '?']:
                    self._show_language_help()
                    
                else:
                    print(f"❌ Invalid choice. Please select from: {', '.join(self.languages.keys())}")
                    print("💡 Type 'help' for more information")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.logger.info("Application terminated by user during language selection")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error during language selection: {e}")
                self.logger.error(f"Language selection error: {e}")
                
    def _show_language_help(self) -> None:
        """Show detailed language selection help"""
        print("\n📖 Language Selection Help")
        print("-" * 40)
        print("Available language codes:")
        for code, lang_info in self.languages.items():
            print(f"  • {code.upper()}: {lang_info['name']} (Speech: {lang_info['code']})")
        print("\nSimply type the 2-letter code and press Enter.")
        print("Example: Type 'en' for English, 'hi' for Hindi")
        
    def speech_to_text(self, prompt_key: str, timeout: int = None, phrase_time_limit: int = None) -> str:
        """
        Convert speech to text with enhanced error handling and user feedback
        
        Args:
            prompt_key: Key for language-specific prompt
            timeout: Listening timeout in seconds
            phrase_time_limit: Maximum phrase duration
            
        Returns:
            Recognized and processed text
        """
        if timeout is None:
            timeout = self.AUDIO_TIMEOUT
        if phrase_time_limit is None:
            phrase_time_limit = self.PHRASE_TIME_LIMIT
            
        # Get language-specific prompt
        prompt_text = self.languages[self.selected_language]['prompts'][prompt_key]
        
        print(f"\n🎤 {prompt_text}")
        self.text_to_speech(prompt_text)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with self.microphone as source:
                    listening_msg = self.languages[self.selected_language]['prompts']['listening']
                    print(f"🔴 {listening_msg}")
                    
                    # Enhanced audio capture
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                
                print("🔄 Processing speech...")
                
                # Get language code for speech recognition
                lang_code = self.languages[self.selected_language]['code']
                
                # Recognize speech with enhanced settings
                text = self.recognizer.recognize_google(
                    audio,
                    language=lang_code,
                    show_all=False
                )
                
                if text.strip():
                    print(f"📝 You said: {text}")
                    
                    # Add punctuation restoration
                    try:
                        punctuated_text = self.punctuation_model.restore_punctuation(text)
                        print(f"📝 With punctuation: {punctuated_text}")
                        self.logger.info(f"Speech recognized: {punctuated_text}")
                        return punctuated_text
                    except Exception as e:
                        self.logger.warning(f"Punctuation restoration failed: {e}")
                        return text
                else:
                    raise sr.UnknownValueError("Empty speech result")
                    
            except sr.WaitTimeoutError:
                retry_count += 1
                timeout_msg = self.languages[self.selected_language]['prompts']['error_timeout']
                print(f"⏰ {timeout_msg}")
                
                if retry_count >= max_retries:
                    print("💡 You can type your response instead:")
                    return input("✏️  Type your answer: ").strip()
                    
            except sr.UnknownValueError:
                retry_count += 1
                error_msg = self.languages[self.selected_language]['prompts']['error_speech']
                print(f"❌ {error_msg}")
                
                if retry_count >= max_retries:
                    print("💡 You can type your response instead:")
                    return input("✏️  Type your answer: ").strip()
                    
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition service error: {e}")
                print(f"❌ Speech recognition service error: {e}")
                print("💡 You can type your response instead:")
                return input("✏️  Type your answer: ").strip()
                
            except Exception as e:
                self.logger.error(f"Unexpected speech recognition error: {e}")
                print(f"❌ Unexpected error: {e}")
                print("💡 You can type your response instead:")
                return input("✏️  Type your answer: ").strip()
                
        # This shouldn't be reached, but just in case
        return input("✏️  Type your answer: ").strip()

    def clean_text_for_speech(self, text: str) -> str:
        """
        Enhanced text cleaning for better TTS clarity
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text suitable for TTS
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Remove emojis and special symbols
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        
        # Remove other special characters and symbols
        text = re.sub(r'[•◦▪▫►▼▲●○■□★☆♠♣♦♥🌾🎤🔴🔄📝⚠️💡❌⏰📋📊🤖🌟💡🤔👋🙏✅❓]', '', text)
        
        # Language-specific symbol replacements
        if self.selected_language:
            replacements = self._get_symbol_replacements()
            for symbol, replacement in replacements.items():
                text = text.replace(symbol, replacement)
        
        # Clean up formatting characters
        text = re.sub(r'\n+', '. ', text)  # Replace newlines with periods
        text = re.sub(r'\t+', ' ', text)   # Replace tabs with spaces
        text = re.sub(r'\s+', ' ', text)   # Replace multiple spaces with single space
        text = text.strip()
        
        # Break very long sentences for better TTS pacing
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                if len(sentence) > 100:
                    parts = sentence.split(',')
                    if len(parts) > 1:
                        cleaned_sentences.extend([part.strip() + ',' for part in parts[:-1]])
                        cleaned_sentences.append(parts[-1].strip())
                    else:
                        cleaned_sentences.append(sentence)
                else:
                    cleaned_sentences.append(sentence)
        
        return ' '.join(cleaned_sentences)

    def _get_symbol_replacements(self) -> Dict[str, str]:
        """Get language-specific symbol replacements for TTS"""
        replacements_map = {
            'en': {
                '&': ' and ', '%': ' percent ', '₹': ' rupees ',
                '°': ' degrees ', '+': ' plus ', '=': ' equals ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' or '
            },
            'hi': {
                '&': ' और ', '%': ' प्रतिशत ', '₹': ' रुपए ',
                '°': ' डिग्री ', '+': ' प्लस ', '=': ' बराबर ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' या '
            },
            'te': {
                '&': ' మరియు ', '%': ' శాతం ', '₹': ' రూపాయలు ',
                '°': ' డిగ్రీలు ', '+': ' ప్లస్ ', '=': ' సమానం ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' లేదా '
            },
            'ta': {
                '&': ' மற்றும் ', '%': ' சதவீதம் ', '₹': ' ரூபாய் ',
                '°': ' பாகைகள் ', '+': ' கூட்டல் ', '=': ' சமம் ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' அல்லது '
            },
            'kn': {
                '&': ' ಮತ್ತು ', '%': ' ಶೇಕಡಾ ', '₹': ' ರೂಪಾಯಿ ',
                '°': ' ಡಿಗ್ರಿ ', '+': ' ಪ್ಲಸ್ ', '=': ' ಸಮ ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' ಅಥವಾ '
            },
            'or': {
                '&': ' ଏବଂ ', '%': ' ଶତକଡ଼ା ', '₹': ' ଟଙ୍କା ',
                '°': ' ଡିଗ୍ରୀ ', '+': ' ପ୍ଲସ ', '=': ' ସମାନ ',
                '*': ' ', '_': ' ', '~': ' ', '^': ' ', '`': ' ',
                '|': ' କିମ୍ବା '
            }
        }
        return replacements_map.get(self.selected_language, replacements_map['en'])

    def text_to_speech(self, text: str) -> None:
        """
        Enhanced text to speech with better clarity and error handling
        
        Args:
            text: Text to convert to speech
        """
        try:
            # Clean text for better TTS
            clean_text = self.clean_text_for_speech(text)
            
            if not clean_text.strip():
                self.logger.warning("No valid text to speak")
                return
                
            # Get TTS language code
            tts_lang = self.languages[self.selected_language]['tts']
            
            # Create TTS object with enhanced settings
            tts = gTTS(
                text=clean_text,
                lang=tts_lang,
                slow=False,
                tld='com'
            )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_filename = tmp_file.name
                tts.save(temp_filename)
            
            # Play audio with enhanced clarity
            self.play_audio_enhanced(temp_filename)
            
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup temp file: {e}")
                
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {e}")
            print(f"⚠️ Text-to-speech error: {e}")
            print(f"📢 Message: {text}")

    def play_audio_enhanced(self, audio_file: str) -> None:
        """
        Play audio file with enhanced clarity and optimal speed
        
        Args:
            audio_file: Path to audio file to play
        """
        system = platform.system().lower()
        
        try:
            if system == "linux":
                # Try mpv with enhanced audio settings
                try:
                    subprocess.run([
                        'mpv',
                        '--speed=1.2',
                        '--volume=100',
                        '--audio-normalize-downmix=yes',
                        '--af=loudnorm',
                        '--no-video',
                        '--really-quiet',
                        audio_file
                    ], check=True, capture_output=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        # Try sox with audio enhancement
                        subprocess.run([
                            'sox', audio_file, '-d',
                            'speed', '1.2',
                            'gain', '-n'
                        ], check=True, capture_output=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to regular playsound
                        playsound(audio_file)
                        
            elif system == "darwin":  # macOS
                try:
                    # Create a temporary sped-up version using sox
                    temp_fast = audio_file.replace('.mp3', '_fast.mp3')
                    subprocess.run([
                        'sox', audio_file, temp_fast, 'speed', '1.2'
                    ], check=True, capture_output=True)
                    playsound(temp_fast)
                    os.unlink(temp_fast)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    playsound(audio_file)
                    
            elif system == "windows":
                try:
                    playsound(audio_file)
                except Exception as e:
                    self.logger.warning(f"Audio playback failed: {e}")
            else:
                playsound(audio_file)
                
        except Exception as e:
            self.logger.error(f"Enhanced audio playback failed: {e}")
            try:
                if playsound:
                    playsound(audio_file)
            except Exception as fallback_error:
                self.logger.error(f"Fallback audio playback failed: {fallback_error}")

    def collect_farmer_data(self) -> None:
        """Collect comprehensive farmer information via speech"""
        print("\n📋 Data Collection Phase")
        print("=" * 40)
        
        processing_msg = self.languages[self.selected_language]['prompts']['processing']
        
        # Data collection steps
        data_steps = [
            ('crop', 'Crop Information'),
            ('soil', 'Soil Type'),
            ('location', 'Location Details'),
            ('history', 'Crop History')
        ]
        
        for step_key, step_name in data_steps:
            print(f"\n📊 Step {data_steps.index((step_key, step_name)) + 1}/4: {step_name}")
            
            try:
                response = self.speech_to_text(step_key)
                self.farmer_data[f'{step_key}_response'] = response
                
                # Validate and clean response
                cleaned_response = self._validate_and_clean_response(step_key, response)
                self.farmer_data[step_key] = cleaned_response
                
                print(f"✅ Recorded: {cleaned_response}")
                
            except Exception as e:
                self.logger.error(f"Error collecting {step_name}: {e}")
                print(f"❌ Error collecting {step_name}: {e}")
                # Provide fallback
                fallback_response = input(f"Please type your {step_name.lower()}: ").strip()
                self.farmer_data[step_key] = fallback_response
        
        # Summary of collected data
        self._display_data_summary()
        
        # Log collected data
        self.logger.info(f"Farmer data collected: {self.farmer_data}")

    def _validate_and_clean_response(self, step_key: str, response: str) -> str:
        """
        Validate and clean user responses
        
        Args:
            step_key: The type of data being collected
            response: Raw user response
            
        Returns:
            Cleaned and validated response
        """
        if not response or not response.strip():
            return "Not specified"
            
        # Basic cleaning
        cleaned = response.strip()
        
        # Step-specific validation
        if step_key == 'crop':
            # Ensure crop name is reasonable
            if len(cleaned) < 2:
                return "Not specified"
        elif step_key == 'location':
            # Ensure location has some geographic info
            if len(cleaned) < 3:
                return "Location not specified"
        
        return cleaned

    def _display_data_summary(self) -> None:
        """Display summary of collected farmer data"""
        print("\n📊 Data Collection Summary")
        print("=" * 40)
        
        summary_items = [
            ("🌱 Crop", self.farmer_data.get('crop', 'N/A')),
            ("🏞️  Soil Type", self.farmer_data.get('soil', 'N/A')),
            ("📍 Location", self.farmer_data.get('location', 'N/A')),
            ("📜 Crop History", self.farmer_data.get('history', 'N/A'))
        ]
        
        for label, value in summary_items:
            print(f"{label}: {value}")
        
        print("=" * 40)

    def generate_dashboard_stats(self) -> Dict[str, str]:
        """Generate comprehensive dashboard statistics using AI"""
        print(f"\n🔄 {self.languages[self.selected_language]['prompts']['processing']}")
        
        # Construct enhanced prompt for dashboard statistics
        dashboard_prompt = self._build_dashboard_prompt()
        
        try:
            stats = self._query_groq_for_stats(dashboard_prompt)
            self.logger.info(f"Dashboard stats generated: {stats}")
            return stats
            
        except APIError as e:
            self.logger.error(f"API error generating dashboard stats: {e}")
            return self._get_fallback_stats()
        except Exception as e:
            self.logger.error(f"Unexpected error generating dashboard stats: {e}")
            return self._get_fallback_stats()

    def _build_dashboard_prompt(self) -> str:
        """Build comprehensive prompt for dashboard statistics"""
        return f"""
        You are an expert agricultural data analyst. Based on the following farmer information, 
        provide ONLY numerical statistics in the exact format requested:

        Farmer Details:
        - Crop: {self.farmer_data.get('crop', 'Unknown')}
        - Soil Type: {self.farmer_data.get('soil', 'Unknown')}
        - Location: {self.farmer_data.get('location', 'Unknown')}
        - Crop History: {self.farmer_data.get('history', 'Unknown')}

        Provide ONLY these statistics in this exact format (numbers only):
        YIELD_PREDICTION: [number] kg/hectare
        IRRIGATION_PERCENTAGE: [number]%
        FERTILIZER_AMOUNT: [number] kg/hectare
        SUCCESS_PROBABILITY: [number]%
        WATER_REQUIREMENT: [number] liters/day
        PESTICIDE_COST: [number] rupees/hectare
        GROWTH_DURATION: [number] days
        MARKET_PRICE: [number] rupees/kg

        Provide realistic estimates based on Indian agricultural conditions, 
        the specific crop, soil type, and location provided.
        """

    def _query_groq_for_stats(self, prompt: str) -> Dict[str, str]:
        """Query Groq API for dashboard statistics"""
        if not self.groq_api_key:
            # In dev without key, return fallback for smooth local runs
            return self._get_fallback_stats()
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an agricultural data analyst. Provide only numerical statistics in the exact format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                self.GROQ_API_URL,
                headers=headers,
                json=data,
                timeout=self.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            stats_text = result['choices'][0]['message']['content']
            
            # Parse the statistics
            stats = {}
            lines = stats_text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    stats[key] = value
            
            return stats
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Groq API request failed: {e}")
        except KeyError as e:
            raise APIError(f"Invalid API response format: {e}")

    def _get_fallback_stats(self) -> Dict[str, str]:
        """Provide fallback statistics when API fails"""
        return {
            'YIELD_PREDICTION': '2500 kg/hectare',
            'IRRIGATION_PERCENTAGE': '75%',
            'FERTILIZER_AMOUNT': '150 kg/hectare',
            'SUCCESS_PROBABILITY': '80%',
            'WATER_REQUIREMENT': '1000 liters/day',
            'PESTICIDE_COST': '3000 rupees/hectare',
            'GROWTH_DURATION': '120 days',
            'MARKET_PRICE': '25 rupees/kg'
        }

    def display_dashboard(self, stats: Dict[str, str]) -> None:
        """Display comprehensive farming dashboard with enhanced visuals"""
        print("\n" + "="*70)
        print("🌾 FARMING DASHBOARD - STATISTICS & PREDICTIONS 🌾")
        print("="*70)
        
        # Get language-specific labels
        labels = self._get_dashboard_labels()
        
        # Display farmer information section
        self._display_farmer_info_section(labels)
        
        # Display predictions and statistics
        self._display_predictions_section(labels, stats)
        
        # Display quick insights
        self._display_insights_section(labels, stats)
        
        print("="*70)

    def _get_dashboard_labels(self) -> Dict[str, str]:
        """Get language-specific dashboard labels"""
        labels_map = {
            'en': {
                'crop_info': 'FARMER INFORMATION',
                'predictions': 'PREDICTIONS & STATISTICS',
                'insights': 'QUICK INSIGHTS',
                'yield': 'Yield Prediction',
                'irrigation': 'Irrigation Requirement',
                'fertilizer': 'Fertilizer Amount',
                'success': 'Success Probability',
                'water': 'Daily Water Requirement',
                'pesticide': 'Pesticide Budget',
                'duration': 'Growth Duration',
                'price': 'Expected Market Price'
            },
            'hi': {
                'crop_info': 'किसान की जानकारी',
                'predictions': 'भविष्यवाणियाँ और सांख्यिकी',
                'insights': 'त्वरित अंतर्दृष्टि',
                'yield': 'उत्पादन पूर्वानुमान',
                'irrigation': 'सिंचाई आवश्यकता',
                'fertilizer': 'उर्वरक की मात्रा',
                'success': 'सफलता की संभावना',
                'water': 'दैनिक पानी की आवश्यकता',
                'pesticide': 'कीटनाशक बजट',
                'duration': 'वृद्धि अवधि',
                'price': 'अपेक्षित बाजार मूल्य'
            }
            # Add other languages as needed...
        }
        return labels_map.get(self.selected_language, labels_map['en'])

    def _display_farmer_info_section(self, labels: Dict[str, str]) -> None:
        """Display farmer information section of dashboard"""
        print(f"\n📊 {labels['crop_info']}")
        print("-" * 40)
        
        info_items = [
            ("🌱 Crop", self.farmer_data.get('crop', 'N/A')),
            ("🏞️  Soil Type", self.farmer_data.get('soil', 'N/A')),
            ("📍 Location", self.farmer_data.get('location', 'N/A')),
            ("📜 Previous Crops", self.farmer_data.get('history', 'N/A'))
        ]
        
        for emoji_label, value in info_items:
            # Truncate long values for better display
            display_value = value if len(value) <= 50 else value[:47] + "..."
            print(f"   {emoji_label}: {display_value}")

    def _display_predictions_section(self, labels: Dict[str, str], stats: Dict[str, str]) -> None:
        """Display predictions and statistics section"""
        print(f"\n📈 {labels['predictions']}")
        print("-" * 40)
        
        # Create visual progress bars
        def create_progress_bar(percentage: float) -> str:
            filled = int(percentage * 20 / 100)
            return "█" * filled + "░" * (20 - filled)
        
        # Extract numerical values for visual bars
        try:
            success_num = float(re.search(r'(\d+(?:\.\d+)?)', 
                                        stats.get('SUCCESS_PROBABILITY', '0')).group(1))
            irrigation_num = float(re.search(r'(\d+(?:\.\d+)?)', 
                                          stats.get('IRRIGATION_PERCENTAGE', '0')).group(1))
        except (AttributeError, ValueError):
            success_num = irrigation_num = 50
        
        # Display key statistics with visual elements
        stat_items = [
            ("🌾", labels['yield'], stats.get('YIELD_PREDICTION', 'N/A'), None),
            ("💧", labels['irrigation'], stats.get('IRRIGATION_PERCENTAGE', 'N/A'), irrigation_num),
            ("🧪", labels['fertilizer'], stats.get('FERTILIZER_AMOUNT', 'N/A'), None),
            ("✅", labels['success'], stats.get('SUCCESS_PROBABILITY', 'N/A'), success_num),
            ("🚿", labels['water'], stats.get('WATER_REQUIREMENT', 'N/A'), None),
            ("🐛", labels['pesticide'], stats.get('PESTICIDE_COST', 'N/A'), None),
            ("⏱️", labels.get('duration', 'Growth Duration'), stats.get('GROWTH_DURATION', 'N/A'), None),
            ("💰", labels.get('price', 'Market Price'), stats.get('MARKET_PRICE', 'N/A'), None)
        ]
        
        for emoji, label, value, progress in stat_items:
            print(f"\n{emoji} {label}: {value}")
            if progress is not None:
                print(f"   Progress: {create_progress_bar(progress)} {progress:.0f}%")

    def _display_insights_section(self, labels: Dict[str, str], stats: Dict[str, str]) -> None:
        """Display quick insights section"""
        print(f"\n🎯 {labels['insights']}")
        print("-" * 20)
        
        # Extract success probability for insights
        try:
            success_num = float(re.search(r'(\d+(?:\.\d+)?)', 
                                        stats.get('SUCCESS_PROBABILITY', '50')).group(1))
            irrigation_num = float(re.search(r'(\d+(?:\.\d+)?)', 
                                          stats.get('IRRIGATION_PERCENTAGE', '50')).group(1))
        except (AttributeError, ValueError):
            success_num = irrigation_num = 50
        
        # Success probability insights
        if success_num >= 80:
            print("🟢 HIGH success probability - Excellent conditions!")
        elif success_num >= 60:
            print("🟡 MODERATE success probability - Good with proper care")
        else:
            print("🔴 LOWER success probability - Requires extra attention")
        
        # Water usage insights
        if irrigation_num <= 50:
            print("💧 LOW water usage - Water-efficient crop")
        elif irrigation_num <= 80:
            print("💧 MODERATE water usage - Standard irrigation needed")
        else:
            print("💧 HIGH water usage - Intensive irrigation required")

    def analyze_crop(self) -> str:
        """Generate comprehensive AI farming analysis"""
        print(f"\n🤖 {self.languages[self.selected_language]['prompts']['processing']}")
        
        analysis_prompt = self._build_analysis_prompt()
        
        try:
            recommendations = self._query_groq_for_analysis(analysis_prompt)
            self.logger.info("Crop analysis completed successfully")
            return recommendations
            
        except APIError as e:
            self.logger.error(f"API error during crop analysis: {e}")
            return self._get_fallback_analysis()
        except Exception as e:
            self.logger.error(f"Unexpected error during crop analysis: {e}")
            return self._get_fallback_analysis()

    def _build_analysis_prompt(self) -> str:
        """Build comprehensive analysis prompt"""
        return f"""
        You are an expert agricultural advisor with deep knowledge of Indian farming conditions.
        Provide comprehensive, practical farming recommendations based on the following information:

        Farmer Profile:
        - Crop to plant: {self.farmer_data.get('crop', 'Unknown')}
        - Soil type: {self.farmer_data.get('soil', 'Unknown')}
        - Location: {self.farmer_data.get('location', 'Unknown')}
        - Previous crop history: {self.farmer_data.get('history', 'Unknown')}

        Please provide detailed, actionable recommendations covering:

        1. YIELD OPTIMIZATION
        - Expected yield range and factors affecting it
        - Best practices to maximize productivity
        - Timing considerations for optimal harvest

        2. IRRIGATION STRATEGY  
        - Optimal watering schedule and methods
        - Water conservation techniques
        - Signs of over/under-watering to watch for

        3. PEST & DISEASE MANAGEMENT
        - Common pests and diseases for this crop in this region
        - Preventive measures and organic solutions
        - When and how to apply treatments

        4. FERTILIZATION PROGRAM
        - Soil preparation and nutrient requirements
        - Organic and chemical fertilizer recommendations
        - Application timing and quantities

        5. SEASONAL CONSIDERATIONS
        - Best planting and harvesting windows
        - Weather-related precautions
        - Market timing strategies

        Make your response practical, specific to Indian conditions, and suitable for 
        farmers with varying experience levels. Keep language simple and actionable.
        """

    def _query_groq_for_analysis(self, prompt: str) -> str:
        """Query Groq API for detailed crop analysis"""
        if not self.groq_api_key:
            return self._get_fallback_analysis()
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert agricultural advisor providing practical, detailed farming recommendations for Indian farmers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.GROQ_API_URL,
                headers=headers,
                json=data,
                timeout=self.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Groq API request failed: {e}")
        except KeyError as e:
            raise APIError(f"Invalid API response format: {e}")

    def _get_fallback_analysis(self) -> str:
        """Provide fallback analysis when API fails"""
        crop = self.farmer_data.get('crop', 'your crop')
        return f"""
        FARMING RECOMMENDATIONS FOR {crop.upper()}

        1. YIELD OPTIMIZATION
        - Expected yield depends on soil quality, weather, and farming practices
        - Focus on soil health improvement and proper spacing
        - Regular monitoring of plant growth is essential

        2. IRRIGATION STRATEGY
        - Maintain consistent moisture levels without waterlogging
        - Water early morning or evening to reduce evaporation
        - Use drip irrigation for water efficiency

        3. PEST & DISEASE MANAGEMENT
        - Regular inspection of plants for early detection
        - Use neem-based organic pesticides as first line of defense
        - Maintain proper plant spacing for air circulation

        4. FERTILIZATION PROGRAM
        - Conduct soil testing before fertilizer application
        - Use organic compost to improve soil structure
        - Follow recommended NPK ratios for your crop

        5. SEASONAL CONSIDERATIONS
        - Plant according to local weather patterns
        - Prepare for monsoon and dry seasons
        - Plan harvest timing for best market prices

        Please consult local agricultural extension officers for region-specific advice.
        """

    def handle_follow_up_queries(self) -> None:
        """Handle follow-up questions with enhanced conversation management"""
        print(f"\n❓ {self.languages[self.selected_language]['prompts']['followup']}")
        
        conversation_history = []
        max_follow_ups = 10
        follow_up_count = 0
        
        while follow_up_count < max_follow_ups:
            try:
                question = self.speech_to_text('followup', timeout=15)
                
                # Check if farmer wants to exit
                if self._is_exit_command(question):
                    thank_you_msg = self.languages[self.selected_language]['prompts']['thank_you']
                    print(f"\n🙏 {thank_you_msg}")
                    self.text_to_speech(thank_you_msg)
                    break
                
                # Log and process question
                print(f"\n🤔 Your question: {question}")
                conversation_history.append({"role": "user", "content": question})
                
                # Get AI answer
                answer = self._get_ai_answer(question, conversation_history)
                
                if answer:
                    print(f"\n💡 AI Response:\n{answer}")
                    conversation_history.append({"role": "assistant", "content": answer})
                    
                    # Split long responses for better TTS
                    self._speak_response_in_chunks(answer)
                    
                    follow_up_count += 1
                    print(f"\n📊 Follow-up {follow_up_count}/{max_follow_ups} completed")
                
            except KeyboardInterrupt:
                print("\n👋 Conversation ended by user")
                break
            except Exception as e:
                self.logger.error(f"Error in follow-up conversation: {e}")
                print(f"❌ Error processing your question: {e}")
                print("Please try asking your question again.")
                
        if follow_up_count >= max_follow_ups:
            print(f"\n⚠️ Maximum follow-up questions ({max_follow_ups}) reached.")
            thank_you_msg = self.languages[self.selected_language]['prompts']['thank_you']
            self.text_to_speech(thank_you_msg)

    def _is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit the conversation"""
        text_lower = text.lower().strip()
        current_exit_words = self.exit_words.get(self.selected_language, self.exit_words['en'])
        return any(word in text_lower for word in current_exit_words)

    def _speak_response_in_chunks(self, text: str, max_chunk_size: int = 200) -> None:
        """Split long text into chunks for better TTS delivery"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        
        for sentence in sentences[:8]:  # Limit to first 8 sentences
            if len(current_chunk + sentence) < max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    self.text_to_speech(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            self.text_to_speech(current_chunk.strip())

    def _get_ai_answer(self, question: str, conversation_history: List[Dict[str, str]]) -> str:
        """Get AI answer for follow-up questions with conversation context"""
        context_prompt = self._build_followup_prompt(question, conversation_history)
        
        try:
            return self._query_groq_for_followup(context_prompt)
        except APIError as e:
            self.logger.error(f"API error during follow-up: {e}")
            return "Sorry, I'm having trouble connecting to the AI service right now. Please try asking your question again."
        except Exception as e:
            self.logger.error(f"Unexpected error during follow-up: {e}")
            return "I apologize, but I couldn't process your question at the moment. Please try rephrasing it."

    def _build_followup_prompt(self, question: str, conversation_history: List[Dict[str, str]]) -> str:
        """Build contextual prompt for follow-up questions"""
        # Get recent conversation context (last 4 exchanges)
        recent_context = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
        context_str = "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in recent_context])
        
        return f"""
        Context: You are providing follow-up advice to a farmer based on their original query.

        Original Farmer Information:
        - Crop: {self.farmer_data.get('crop', 'Unknown')}
        - Soil: {self.farmer_data.get('soil', 'Unknown')}
        - Location: {self.farmer_data.get('location', 'Unknown')}
        - History: {self.farmer_data.get('history', 'Unknown')}

        Recent Conversation:
        {context_str}

        Current Question: {question}

        Please provide a helpful, concise, and practical answer related to farming advice.
        Keep the response focused, actionable, and suitable for farmers.
        If the question is not related to farming, politely redirect to agricultural topics.
        """

    def _query_groq_for_followup(self, prompt: str) -> str:
        """Query Groq API for follow-up responses"""
        if not self.groq_api_key:
            return "I'm running in local demo mode without AI. Please set GROQ_API_KEY in .env for live answers."
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.GROQ_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful agricultural expert providing follow-up advice to farmers. Keep responses practical, concise, and farmer-friendly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 800,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                self.GROQ_API_URL,
                headers=headers,
                json=data,
                timeout=self.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise APIError(f"Groq API request failed: {e}")
        except KeyError as e:
            raise APIError(f"Invalid API response format: {e}")

    def save_session_data(self) -> None:
        """Save session data for future reference"""
        try:
            session_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'language': self.selected_language,
                'farmer_data': self.farmer_data,
                'status': 'completed'
            }
            
            # Create sessions directory if it doesn't exist
            os.makedirs('sessions', exist_ok=True)
            
            # Save session data
            session_file = f"sessions/session_{self.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Session data saved: {session_file}")
            print(f"📁 Session saved: {session_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
            print(f"⚠️ Could not save session data: {e}")

    # --- API Endpoints for Bolt UI Integration ---

"""
Flask app and CORS configuration
- FRONTEND_ORIGINS: comma-separated list of allowed origins for the frontend
    Defaults to typical Vite dev ports: http://localhost:5173 and http://127.0.0.1:5173
- BACKEND_HOST: host to bind Flask app (default 0.0.0.0)
- BACKEND_PORT: port to run Flask app (default 5000)
"""

# Ensure .env is loaded before reading env vars here
load_dotenv()

app = Flask(__name__)

# --- CORS: allow any localhost port + optional explicit env origins ---
frontend_origins_env = os.getenv('FRONTEND_ORIGINS') or os.getenv('FRONTEND_ORIGIN')
env_origins = [o.strip() for o in frontend_origins_env.split(',')] if frontend_origins_env else []

# Allow any localhost/127.0.0.1 port during dev (use compiled regex)
allowed_origins = [
    re.compile(r"http://localhost:\d+$"),
    re.compile(r"http://127\.0\.0\.1:\d+$"),
    *[o for o in env_origins if o],
]

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

def _origins_to_str(origins) -> str:
    try:
        return ', '.join(getattr(o, 'pattern', o) for o in origins)
    except Exception:
        return str(origins)

def _is_origin_allowed(origin: Optional[str]) -> bool:
    if not origin:
        return False
    for o in allowed_origins:
        if hasattr(o, "match"):  # regex
            if o.match(origin):
                return True
        elif origin == o:
            return True
    return False

advisor_instance = None

@app.before_request
def _ensure_advisor():
    global advisor_instance
    if advisor_instance is None:
        advisor_instance = FarmingAdvisor()
        # Ensure a default language for API requests (avoids None references)
        try:
            default_lang = os.getenv('DEFAULT_LANGUAGE', 'en').strip().lower()
            if default_lang not in advisor_instance.languages:
                default_lang = 'en'
            advisor_instance.selected_language = default_lang
        except Exception:
            advisor_instance.selected_language = 'en'
        app.logger.info("[BOOT] Advisor initialized. CORS=%s", _origins_to_str(allowed_origins))

# Replace the previous _log_req with this one
@app.before_request
def _log_req():
    origin = request.headers.get('Origin')
    app.logger.info("[REQ] %s %s Origin=%s Allowed=%s",
                    request.method, request.path, origin, _is_origin_allowed(origin))

@app.after_request
def _log_res(resp):
    app.logger.info("[RES] %s %s -> %s Allow-Origin=%s",
                    request.method, request.path, resp.status,
                    resp.headers.get('Access-Control-Allow-Origin'))
    return resp

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat() + "Z"})

# NEW: Endpoint to get full recommendations from either structured fields or free-form text
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(silent=True) or {}
    lang = (data.get("language") or "en").strip().lower()
    if advisor_instance and lang in advisor_instance.languages:
        advisor_instance.selected_language = lang

    # If structured fields are provided, use them; otherwise use free-form text
    crop = (data.get("crop") or "").strip()
    soil = (data.get("soil") or "").strip()
    location = (data.get("location") or "").strip()
    history = (data.get("history") or "").strip()
    free_text = (data.get("text") or "").strip()

    if any([crop, soil, location, history]):
        # Update the in-memory farmer data and use the structured analysis
        advisor_instance.farmer_data.update({
            "crop": crop or advisor_instance.farmer_data.get("crop", ""),
            "soil": soil or advisor_instance.farmer_data.get("soil", ""),
            "location": location or advisor_instance.farmer_data.get("location", ""),
            "history": history or advisor_instance.farmer_data.get("history", ""),
        })
        rec = advisor_instance.analyze_crop()
    elif free_text:
        rec = advisor_instance.analyze_from_text(free_text)
    else:
        return jsonify({"error": "Provide either text or crop/soil/location/history"}), 400

    # Optionally also return quick stats if requested
    if str(data.get("withStats", "")).lower() in ("1", "true", "yes"):
        stats = advisor_instance.generate_dashboard_stats()
        return jsonify({"recommendations": rec, "stats": stats}), 200

    return jsonify({"recommendations": rec}), 200

# REPLACE: stubbed followup endpoint with real AI-backed Q&A and session history
@app.route("/followup", methods=["POST"])
def followup():
    try:
        data = request.get_json(silent=True) or {}
        # Accept either "question" or "text" from the chat UI
        question = (data.get("question") or data.get("text") or "").strip()
        lang = (data.get("language") or "en").strip().lower()

        if not question:
            return jsonify({"error": "Missing 'question' or 'text'"}), 400

        if advisor_instance and lang in advisor_instance.languages:
            advisor_instance.selected_language = lang

        # Directly generate recommendations from the chat text
        answer = advisor_instance.analyze_from_text(question)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        app.logger.exception("Error in /followup")
        return jsonify({"error": "Internal error", "details": str(e)}), 500

    def analyze_from_text(self, text: str) -> str:
        """
        Produce practical farming recommendations from a free-form message.
        Attempts a simple crop inference to improve fallback output.
        """
        try:
            msg = (text or "").strip()
            # Heuristic: infer crop from verbs or known crop keywords
            try:
                m = re.search(
                    r'\b(grow|plant|cultivate|sow)\s+(?:a|an|the|some)?\s*([a-zA-Z][a-zA-Z\s-]{1,40})',
                    msg,
                    flags=re.IGNORECASE
                )
                crop = None
                if m:
                    crop = m.group(2).strip()
                else:
                    known = [
                        "paddy","rice","wheat","maize","corn","cotton","sugarcane","millet","bajra",
                        "jowar","ragi","soybean","mustard","groundnut","peanut","chickpea","gram",
                        "tur","pigeon pea","lentil","banana","tomato","potato","onion","chili","chilli"
                    ]
                    for k in known:
                        if re.search(rf'\b{k}\b', msg, flags=re.IGNORECASE):
                            crop = k
                            break
                if crop:
                    self.farmer_data['crop'] = crop
            except Exception:
                pass

            prompt = f"""
            You are an expert agricultural advisor with deep knowledge of Indian farming conditions.
            A farmer sent the following details in one message. Provide comprehensive, practical recommendations.

            Free-form farmer message:
            {msg}

            If possible, infer:
            - Crop to plant
            - Soil type
            - Location
            - Previous crop history

            Then provide clear, actionable advice covering:
            - Yield optimization
            - Irrigation strategy
            - Pest & disease management
            - Fertilization program
            - Seasonal considerations

            Keep the response practical, Indian context-specific, and farmer-friendly.
            """
            return self._query_groq_for_analysis(prompt)
        except Exception:
            return self._get_fallback_analysis()

if __name__ == "__main__":
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    port = int(os.getenv('BACKEND_PORT', '5000'))
    print(f"Starting backend on {host}:{port}; allowed CORS origins: {_origins_to_str(allowed_origins)}")
    app.run(host=host, port=port)