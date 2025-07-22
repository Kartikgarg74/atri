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

        self.logger.info(f"Sarika Pandey Bot initialized for: {self.user_data['name']}")

    def create_optimized_prompt(self, user_query, is_follow_up=False):
        """Create the ultra-optimized prompt based on PDF requirements and our research"""

        # Generate real-time birth chart
        chart_data = self.calculator.generate_birth_chart(
            self.user_data['dob'],
            self.user_data['time'],
            self.user_data['location'],
            self.user_data['coordinates']
        )

        # Multi-turn context management
        context_summary = ""
        conversation_thread = ""

        if is_follow_up and self.conversation_history:
            # Get last 2 exchanges for context (optimized as per our analysis)
            recent_exchanges = self.conversation_history[-4:]
            context_summary = " | ".join([f"{msg['role']}: {msg['content'][:35]}..."
                                        for msg in recent_exchanges])

            # Identify conversation thread (Canada, career, marriage, etc.)
            last_user_msg = next((msg['content'] for msg in reversed(self.conversation_history)
                                if msg['role'] == 'user'), "")
            if any(word in last_user_msg.lower() for word in ['canada', 'foreign', 'abroad', 'visa']):
                conversation_thread = "FOREIGN_SETTLEMENT"
            elif any(word in last_user_msg.lower() for word in ['job', 'career', 'work', 'profession']):
                conversation_thread = "CAREER"
            elif any(word in last_user_msg.lower() for word in ['marriage', 'wedding', 'partner', 'love']):
                conversation_thread = "MARRIAGE"

        # Ultra-optimized prompt (reduced from 15,000+ tokens to ~600 tokens as analyzed)
        prompt = f"""You are {self.astrologer_data['name']}, {self.astrologer_data['age']}-year-old Vedic astrologer from {self.astrologer_data['location']} with {self.astrologer_data['experience']}+ years experience. Speak Hindi-English mix, wise but simple for youth. No "beta/dear". Avoid death/disaster predictions.

**BIRTH DATA - {self.user_data['name']}:**
Born: {self.user_data['dob']} at {self.user_data['time']}, {self.user_data['location']}
Ayanamsa: {chart_data['ayanamsa']:.1f}°

**ASCENDANT:** {chart_data['ascendant']['sign']} {chart_data['ascendant']['degree']:.1f}° in {chart_data['ascendant']['nakshatra']}

**KEY PLANETS:**
- Sun: {chart_data['planets']['Sun']['sign']} (H{chart_data['planets']['Sun']['house']})
- Moon: {chart_data['planets']['Moon']['sign']} (H{chart_data['planets']['Moon']['house']})
- Jupiter: {chart_data['planets']['Jupiter']['sign']} (H{chart_data['planets']['Jupiter']['house']})
- Venus: {chart_data['planets']['Venus']['sign']} (H{chart_data['planets']['Venus']['house']})
- Mars: {chart_data['planets']['Mars']['sign']} (H{chart_data['planets']['Mars']['house']})
- Rahu: {chart_data['planets']['Rahu']['sign']} (H{chart_data['planets']['Rahu']['house']})

**CURRENT DASHA:** {chart_data['current_dasha']['mahadasha_lord']} Mahadasha

**ACTIVE YOGAS:** {', '.join(chart_data['yogas'][:2])}

{"**CONTEXT:** " + context_summary if is_follow_up else "**NEW CONVERSATION**"}
{"**THREAD:** " + conversation_thread if conversation_thread else ""}

**CORE RULES:**
- Respond under 120 words ONLY
- Use simple Hindi-English mix
- Break with "/n" for readability
- End with follow-up question
- Reference specific chart elements

**RESPONSE PATTERN (from PDF examples):**
1. Identify chart combination: "Aapke chart mein [planet/yoga] hai..."
2. Connect to dasha: "[Current dasha] mein [effect]..."
3. Give timeline: "[Specific months/years] tak [prediction]..."
4. Simple remedy if asked: "Upay: [basic remedy]..."
5. Follow-up question: "[Engaging question]?"

USER QUERY: {user_query}

Analyze chart above. Reference specific planets/houses/yogas. Stay under 120 words. End with question.

**Disclaimer:** Interpretive insights based on Vedic traditions; consult professionals for major decisions."""

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

    def reset_conversation(self):
        """Reset conversation history for new session"""
        self.conversation_history = []
        return "Conversation history cleared! Ready for fresh questions."

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
                    print(bot.reset_conversation())
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
