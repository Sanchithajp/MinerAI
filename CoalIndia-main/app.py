import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import re
import speech_recognition as sr
import pyttsx3
from deep_translator import GoogleTranslator

def translate_text(text, target_lang):
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I could not understand."
        except sr.RequestError:
            return "Speech service unavailable."

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def main():
    # Get Groq API key
    groq_api_key = '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'

    # Set up Streamlit interface
    st.title("MinerAI!")
    st.sidebar.title('Customization')

    # Add customization options to the sidebar
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama-3.3-70b-versatile']
    )

    st.sidebar.title("Choose a Persona")
    personas = {
        "Virtual Geologist": "🪨 Geologist",
        "Safety and Regulatory Officer": "⚠️ Safety and Regulatory Officer",
        "Equipment Specialist": "🔧 Equipment Expert",
        "Environmental Analyst": "🌱 Environmental Analyst"
    }

    if "selected_persona" not in st.session_state:
        st.session_state.selected_persona = None

    for key, label in personas.items():
        if st.sidebar.button(label):
            st.session_state.selected_persona = key  # Store selected persona

    if not st.session_state.selected_persona:
        st.write("👈 Select a persona from the sidebar to start chatting!")
        return

    st.write(f"🤖 **{st.session_state.selected_persona} is ready to chat!**")

    # Persona-specific prompts
    persona_prompts = {
        "Virtual Geologist": (
            "You are a geologist. ONLY answer questions about rocks, minerals, coal deposits, "
            "geological surveys, and related topics. If a question is outside geology, "
            "politely say you can only answer geological questions."
        ),
        "Safety and Regulatory Officer": (
            "You are a mining safety and regulatory officer. ONLY answer questions about safety rules, risk assessment, laws, regulations, acts, or recent policy updates,"
            "protective gear, and emergency procedures. If a question is outside safety, "
            "politely say you can only answer mining safety-related questions."
        ),
        "Equipment Specialist": (
            "You are a mining equipment expert. ONLY answer questions about mining machinery, "
            "maintenance, and equipment troubleshooting. If a question is outside mining equipment, "
            "politely say you can only discuss machinery."
        ),
        "Environmental Analyst": (
            "You are an environmental analyst. ONLY answer questions about sustainability, pollution control, "
            "and mining's environmental impact. If a question is outside environmental concerns, "
            "politely say you can only discuss eco-friendly mining."
        ),
       
    }

    # Define allowed topics **outside** the if block to avoid UnboundLocalError
    allowed_topics = {
        "Virtual Geologist": [
        "geology", "earth science", "rock formations", "geological time scale", "plate tectonics", 
        "geological mapping", "sedimentary rocks", "igneous rocks", "metamorphic rocks", "quartz", 
        "feldspar", "calcite", "gypsum", "coal seams", "ore bodies", "mineral veins", "geological mapping",
        "core drilling", "borehole analysis", "geophysical surveys", "ground-penetrating radar", 
        "seismic exploration", "magnetic anomaly detection", "mineral exploration techniques", "stratigraphy", 
        "fault lines", "earth layers", "mineral deposits", "ore extraction", "resource estimation", 
        "mine planning", "sedimentation patterns", "geomechanics", "rock mass classification", 
        "underground stability assessment", "geological compass", "microscopes for petrology", 
        "seismic sensors", "remote sensing", "GIS mapping in geology", "3D geological modeling",
        "coal mining geology", "gold mining geology", "oil and gas reservoirs", "mineral resource evaluation",
        "geothermal energy exploration"
    ],
    "Safety and Regulatory Officer": [
        "safety regulations", "risk management", "hazard assessment", "industrial safety", 
        "emergency protocols", "safety compliance", "workplace safety", "mine ventilation", 
        "mine collapse prevention", "dust suppression", "mine lighting standards", "confined space entry", 
        "rockfall protection", "explosive handling", "mine rescue procedures", "PPE (personal protective equipment)",
        "fire safety", "first aid", "OSHA regulations", "MSHA (Mine Safety and Health Administration)", 
        "accident prevention", "toxic exposure", "respiratory protection", "emergency response plans",
        "electrical safety in mining", "fall protection", "safety training programs", "heat stress prevention",
        "fatigue management", "blasting safety","safety measures","mining laws", "safety regulations", "environmental compliance", "OSHA standards", "MSHA policies", 
         "mining safety acts", "mine closure regulations", "worker rights", "permits for mining operations", 
        "government policies on mining", "land acquisition rules", "recent amendments in mining laws", 
        "mining tax laws", "international mining regulations", "corporate social responsibility in mining"
    ],
    "Equipment Specialist": [
        "heavy machinery", "drilling equipment", "excavators", "bulldozers", "loaders", "conveyor belts", 
        "hydraulic systems", "gear mechanisms", "automation in mining", "robotics in mining", "wear and tear analysis",
        "lubrication systems", "sensor-based maintenance", "IoT in mining equipment", "predictive maintenance",
        "spare parts management", "equipment efficiency", "power systems", "mechanical diagnostics",
        "vibration analysis", "mining truck maintenance", "drill rig operation", "underground haulage",
        "belt conveyor systems", "equipment downtime reduction"
    ],
    "Environmental Analyst": [
        "environmental impact assessment (EIA)", "water contamination", "air quality monitoring", 
        "carbon footprint", "green mining techniques", "mine reclamation", "soil erosion", "wildlife conservation", 
        "waste management", "renewable energy in mining", "reforestation", "sustainable resource management", 
        "climate change mitigation", "bioremediation", "toxic waste disposal", "biodiversity protection",
        "ecological balance", "pollution control", "mine closure planning", "tailings management",
        "sustainable extraction methods", "land rehabilitation", "energy-efficient mining"
    ],
    
    }

    language = st.sidebar.selectbox("Choose language", ['en', 'hi', 'ta', 'te', 'kn', 'ml'])
    
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)
    memory = ConversationBufferWindowMemory(k=conversational_memory_length)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    use_voice_input = st.sidebar.button("Use voice input")
    if use_voice_input:
        user_question = recognize_speech()
    else:
        user_question = st.chat_input("Ask a question:")
    
    for message in st.session_state.chat_history[-10:]:
        st.chat_message("User").markdown(message['human'])
        st.chat_message("CoalExpert").markdown(message['AI'])
    
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    conversation = ConversationChain(llm=groq_chat, memory=memory)
    
    if user_question:
        translated_input = GoogleTranslator(source='auto', target='en').translate(user_question)
        selected_persona = st.session_state.selected_persona
        
        full_prompt = f"{persona_prompts[selected_persona]}\nUser Question: {translated_input}"
        response_text = conversation.run(full_prompt)
        translated_response = GoogleTranslator(source='en', target=language).translate(response_text)
        
        message = {'human': user_question, 'AI': translated_response}
        st.session_state.chat_history.append(message)
        
        st.chat_message("User").markdown(message['human'])
        st.write("Chatbot:", translated_response)
        
        speak_text(translated_response)

if __name__ == "__main__":
    main()
