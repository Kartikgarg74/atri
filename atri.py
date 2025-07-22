"""
Enhanced Vedic Astrology Chatbot - Main Implementation
Following the modular project structure with all optimizations
"""

import os
import logging
from datetime import datetime
import google.generativeai as genai
from config import config
from astrology_calculator import VedicAstrologyCalculator

class SarikaPandeyBot:
    def __init__(self):
        """Initialize the Sarika Pandey astrology chatbot"""
        self.logger = logging.getLogger(__name__)

        # Configure Gemini API using config
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)

        # Initialize components
        self.calculator = VedicAstrologyCalculator()
        self.conversation_history = []

        # Load user and astrologer data from config
        self.user_data = config.user_data
        self.astrologer_data = config.astrologer_data

        # Language state tracking
        self.current_language = None
        self.conversation_started = False
        self.introduction_given = False

        self.logger.info(f"Sarika Pandey Bot initialized for: {self.user_data['name']}")

    def detect_language(self, user_input):
        """Enhanced language detection for Hindi, English, and Hinglish"""
        # Convert to uppercase for easier checking
        text = user_input.upper()

        # Common Hinglish/Hindi words in Roman script
        hindi_roman_words = {
            'MERA', 'TERA', 'APNA', 'KAISE', 'KAISE', 'KAHAN', 'KYON', 'KYA',
            'HAI', 'HO', 'HOGA', 'HOGEGA', 'JANE', 'AANE', 'DESH', 'GHAR',
            'PAISA', 'NAUKRI', 'SHAADI', 'RISHTA', 'BACHHE', 'MATA', 'PITA',
            'BHAGWAN', 'MANDIR', 'PUJA', 'VYAAH', 'YOG', 'YOGA', 'KAAM',
            'PADHAI', 'SIKSHA', 'HEALTH', 'SEHAT', 'DUKAAN', 'BUSINESS',
            'FOREIGN', 'BAHAR', 'BHR', 'VIDESH', 'AMERICA', 'CANADA',
            'PAISE', 'RUPAYE', 'LAKHS', 'CRORE', 'HAZAR', 'SAL', 'SAAL',
            'MAHINE', 'DIN', 'RAAT', 'SUBAH', 'SHAM', 'DOPHAR'
        }

        # Check for Devanagari characters
        hindi_chars = sum(1 for char in user_input if '\u0900' <= char <= '\u097F')

        # Check for Hindi words in Roman script
        words = text.split()
        hindi_roman_count = sum(1 for word in words if any(hw in word for hw in hindi_roman_words))

        # Check for English-only words
        english_words = {
            'THE', 'IS', 'ARE', 'WILL', 'SHALL', 'CAN', 'COULD', 'WOULD',
            'SHOULD', 'MY', 'YOUR', 'HIS', 'HER', 'WHEN', 'WHERE', 'HOW',
            'WHAT', 'WHY', 'AND', 'OR', 'BUT', 'WITH', 'FROM', 'TO', 'IN',
            'ON', 'AT', 'BY', 'FOR', 'OF', 'AS', 'LIKE', 'THAN', 'SUCH'
        }

        english_word_count = sum(1 for word in words if word in english_words)
        total_words = len(words)

        # Decision logic
        if hindi_chars > 0:
            return "hindi"
        elif hindi_roman_count > 0 or (hindi_roman_count + english_word_count) < total_words:
            return "hinglish"
        elif english_word_count >= total_words * 0.4:
            return "english"
        else:
            return "hinglish"  # Default to hinglish for mixed content

    def create_optimized_prompt(self, user_query, is_follow_up=False):
        """Create language-aware optimized prompt without repetitive introductions"""

        # Detect current query language
        detected_language = self.detect_language(user_query)

        # Check if this is truly a new conversation or language switch
        language_switched = (self.current_language is not None and
                            self.current_language != detected_language)

        # Update current language
        self.current_language = detected_language

        # Generate real-time birth chart
        chart_data = self.calculator.generate_birth_chart(
            self.user_data['dob'],
            self.user_data['time'],
            self.user_data['location'],
            self.user_data['coordinates']
        )

        # Multi-turn context management
        context_summary = ""
        if is_follow_up and self.conversation_history:
            recent_exchanges = self.conversation_history[-4:]
            context_summary = " | ".join([f"{msg['role']}: {msg['content'][:35]}..."
                                        for msg in recent_exchanges])

        # Language-specific instructions
        if detected_language == "hindi":
            language_rules = """
**LANGUAGE & CONTEXT RULES:**
- User ne Hindi mein sawal kiya hai, respond ONLY in Hindi
- Use Devanagari script appropriately
- Chart reference: "Aapke chart mein" (NOT "आपकी कुंडली के अनुसार")
- Follow-up question: "Kya aapko apne vishay mein kuch aur sawal hai?"
- NO introduction if conversation already started
- Be conversational, not formal
"""
        elif detected_language == "english":
            language_rules = """
**LANGUAGE & CONTEXT RULES:**
- User asked in English, respond ONLY in English
- Chart reference: "Your chart shows"
- Follow-up question: "Do you have any other questions about your topic?"
- NO introduction if conversation already started
- Maintain professional but friendly tone
"""
        else:  # hinglish
            language_rules = """
**LANGUAGE & CONTEXT RULES:**
- User used Hinglish/Roman Hindi, respond in NATURAL HINGLISH
- Mix Hindi and English naturally: "Aapke chart mein" not "Based on Kartik's chart"
- Use Roman script for Hindi words (MERA = your, DESH = country, etc.)
- Follow-up question: "Kya aapko is baare mein aur kuch puchna hai?"
- NO introduction if conversation already started
- Natural Hindi-English mixing like: "Aapke chart mein strong yogas hain"
"""

        # Determine if introduction is needed
        needs_introduction = (not self.conversation_started and not is_follow_up)

        # Mark conversation as started
        if not self.conversation_started:
            self.conversation_started = True

        # Create introduction text
        if needs_introduction:
            if detected_language == "hindi":
                intro_text = "Namaste, main Sarika Pandey hun, Lucknow se aapki Vedic astrologer."
            elif detected_language == "english":
                intro_text = "Hello, I'm Sarika Pandey, your Vedic astrologer from Lucknow."
            else:  # hinglish
                intro_text = "Namaste, main Sarika Pandey hun, aapki astrologer."
        else:
            intro_text = ""

        # Ultra-optimized prompt
        prompt = f"""You are Sarika Pandey, 20-year-old Vedic astrologer from Lucknow with 18+ years experience.

{language_rules}

**BIRTH DATA - {self.user_data['name']}:**
Born: {self.user_data['dob']} at {self.user_data['time']}, {self.user_data['location']}
Ayanamsa: {chart_data['ayanamsa']:.1f}°

**ASCENDANT:** {chart_data['ascendant']['sign']} {chart_data['ascendant']['degree']:.1f}° in {chart_data['ascendant']['nakshatra']}

**KEY PLANETS:**
- Sun: {chart_data['planets']['Sun']['sign']} (H{chart_data['planets']['Sun']['house']})
- Moon: {chart_data['planets']['Moon']['sign']} (H{chart_data['planets']['Moon']['house']})
- Jupiter: {chart_data['planets']['Jupiter']['sign']} (H{chart_data['planets']['Jupiter']['house']})
- Venus: {chart_data['planets']['Venus']['sign']} (H{chart_data['planets']['Venus']['house']})
- Rahu: {chart_data['planets']['Rahu']['sign']} (H{chart_data['planets']['Rahu']['house']})

**CURRENT DASHA:** {chart_data['current_dasha']['mahadasha_lord']} Mahadasha

{"**CONTEXT:** " + context_summary if is_follow_up else "**NEW CONVERSATION**"}

**INTRODUCTION:** {intro_text if intro_text else "Continue conversation naturally without introduction"}

**CORE RULES:**
- Respond under 120 words ONLY
- Break with "/n" for readability
- End with appropriate follow-up question based on language
- Reference chart using language-specific format above
- NO repetitive introductions in ongoing conversation
- For HINGLISH: Use natural mixing like "Aapke chart mein foreign travel ke strong chances hain"

USER QUERY: {user_query}

{"Start with introduction, then " if intro_text else ""}Analyze chart and respond in DETECTED LANGUAGE ({detected_language.upper()}). Stay under 120 words.
"""

        return prompt

    def chat(self, user_input):
        """Main chat function with comprehensive error handling"""
        try:
            # Determine if this is a follow-up conversation
            is_follow_up = len(self.conversation_history) > 0

            # Generate the optimized prompt
            prompt = self.create_optimized_prompt(user_input, is_follow_up)

            # Call Gemini API with configuration settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config.api_temperature,
                    top_p=config.api_top_p,
                    top_k=config.api_top_k,
                    max_output_tokens=config.max_output_tokens,
                )
            )

            # Extract response text
            assistant_response = response.text if hasattr(response, 'text') else str(response)

            # Update conversation history with size limits
            self._update_conversation_history(user_input, assistant_response)

            return assistant_response

        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return self._get_graceful_error_response()

    def _update_conversation_history(self, user_input, assistant_response):
        """Update conversation history with smart truncation"""
        self.conversation_history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_response}
        ])

        # Keep only recent exchanges as per configuration
        max_history = config.max_conversation_history
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]

    def _get_graceful_error_response(self):
        """Return graceful error response in Sarika's style"""
        return (
            f"मुझे खुशी होगी आपकी मदद करने में। /n "
            f"कृपया अपना सवाल दोबारा पूछें। /n "
            f"क्या आप किसी खास विषय के बारे में जानना चाहते हैं?"
        )

    def get_chart_summary(self):
        """Generate detailed birth chart summary"""
        try:
            chart_data = self.calculator.generate_birth_chart(
                self.user_data['dob'],
                self.user_data['time'],
                self.user_data['location'],
                self.user_data['coordinates']
            )

            summary = f"""
═══════════════════════════════════════════════════════════
🔮 **{self.astrologer_data['name'].upper()} - BIRTH CHART ANALYSIS** 🔮
═══════════════════════════════════════════════════════════

**Native Details:**
📅 Name: {self.user_data['name']}
🕐 Born: {self.user_data['dob']} at {self.user_data['time']}
📍 Location: {self.user_data['location']}
🌟 Ayanamsa: {chart_data['ayanamsa']:.2f}°

**Lagna (Ascendant):**
🏠 {chart_data['ascendant']['sign']} {chart_data['ascendant']['degree']:.1f}° in {chart_data['ascendant']['nakshatra']} Nakshatra

**Current Dasha Period:**
⏰ {chart_data['current_dasha']['mahadasha_lord']} Mahadasha (Balance: {chart_data['current_dasha']['balance_years']:.1f} years)

**Planetary Positions:**"""

            for planet, data in chart_data['planets'].items():
                summary += f"\n🪐 {planet}: {data['sign']} {data['degree']:.1f}° (House {data['house']}) - {data['nakshatra']}"

            summary += f"\n\n**Active Yogas:**"
            for yoga in chart_data['yogas']:
                summary += f"\n✨ {yoga}"

            summary += "\n\n═══════════════════════════════════════════════════════════"

            return summary

        except Exception as e:
            self.logger.error(f"Chart summary error: {e}")
            return "Chart data temporarily unavailable. Please try again."

    def reset_conversation_state(self):
        """Reset conversation state for new session"""
        self.conversation_history = []
        self.current_language = None
        self.conversation_started = False
        self.introduction_given = False
        return "Conversation reset! Ready for fresh questions."

def main():
    """Main function to run the Sarika Pandey chatbot"""

    # Display startup banner
    print("🔮" + "="*65 + "🔮")
    print(f"    {config.astrologer_data['name'].upper()} - VEDIC ASTROLOGY CHATBOT")
    print(f"    Enhanced for: {config.user_data['name']}")
    print(f"    Powered by Real Math & Gemini {config.gemini_model}")
    print("🔮" + "="*65 + "🔮")

    try:
        # Initialize the chatbot
        bot = SarikaPandeyBot()

        # Display birth chart summary
        print(bot.get_chart_summary())

        # Instructions
        print("\n📝 **How to Use:**")
        print("• Ask about career, marriage, health, finances, Canada settlement")
        print("• Type 'chart' to see birth chart again")
        print("• Type 'reset' to clear conversation history")
        print("• Type 'quit'/'exit'/'bye' to end session")
        print("\n" + "="*65)

        # Main chat loop
        while True:
            try:
                user_input = input(f"\n🙏 **Your Question:** ").strip()

                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print(f"\n🙏 **{config.astrologer_data['name']}:** धन्यवाद! आपका भविष्य उज्जवल हो!")
                    print("✨ May the stars guide you on your journey! ✨")
                    break

                elif user_input.lower() == 'chart':
                    print(bot.get_chart_summary())
                    continue

                elif user_input.lower() == 'reset':
                    print(bot.reset_conversation_state())
                    continue

                elif not user_input:
                    print("कृपया अपना सवाल पूछें।")
                    continue

                # Process the question
                print(f"\n🔮 **{config.astrologer_data['name']}:** ", end="")
                response = bot.chat(user_input)

                # Format response with proper line breaks
                formatted_response = response.replace("/n", f"\n{' '*21}")
                print(formatted_response)

            except KeyboardInterrupt:
                print(f"\n\n🙏 Session ended. May the stars bless you! ✨")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("कृपया अपना सवाल दोबारा पूछें।")

    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("Please check your configuration and API key.")

    finally:
        print("\n" + "="*65)

if __name__ == "__main__":
    main()
