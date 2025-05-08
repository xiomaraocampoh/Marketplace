import os
import openai
from dotenv import load_dotenv
from django.conf import settings

# Cargar variables de entorno
load_dotenv()

# Configurar la API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class AIService:
    """Servicio para interactuar con la API de OpenAI"""
    
    @staticmethod
    def get_chatbot_response(message, context=None):
        """
        Obtiene una respuesta del chatbot usando OpenAI API
        
        Args:
            message (str): Mensaje del usuario
            context (dict, optional): Contexto adicional para la consulta
        
        Returns:
            str: Respuesta generada por la IA
        """
        try:
            # Preparar el sistema y el contexto
            system_message = (
                "Eres un asistente amigable para un marketplace en línea. "
                "Puedes ayudar con preguntas sobre productos, el proceso de compra, "
                "políticas de devolución y sugerir productos. "
                "Mantén tus respuestas breves y útiles."
            )
            
            # Inicializar la lista de mensajes
            messages = [{"role": "system", "content": system_message}]
            
            # Añadir contexto si existe
            if context:
                if 'products' in context:
                    product_list = ", ".join([p.name for p in context['products']])
                    messages.append({
                        "role": "system", 
                        "content": f"Los siguientes productos están disponibles: {product_list}"
                    })
                
                if 'user' in context and context['user'].is_authenticated:
                    if 'cart_items' in context:
                        if context['cart_items'].exists():
                            cart_list = ", ".join([f"{item.product.name} (cantidad: {item.quantity})" 
                                                for item in context['cart_items']])
                            messages.append({
                                "role": "system", 
                                "content": f"El usuario tiene estos productos en su carrito: {cart_list}"
                            })
                        else:
                            messages.append({
                                "role": "system", 
                                "content": "El carrito del usuario está vacío."
                            })
            
            # Añadir el mensaje del usuario
            messages.append({"role": "user", "content": message})
            
            # Llamar a la API de OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Puedes actualizar a un modelo más reciente si es necesario
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            # Devolver la respuesta
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # En caso de error, devolver un mensaje de error
            print(f"Error en AIService: {str(e)}")
            return "Lo siento, estoy teniendo dificultades técnicas en este momento. Por favor, intenta de nuevo más tarde."