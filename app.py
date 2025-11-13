import pandas as pd
import gradio as gr
import google.generativeai as genai
import os

## REVIEWS - RESTAURANTES

# =====================================================
# 1. CONFIGURAÇÃO DO GEMINI
# =====================================================
# Para Hugging Face Spaces: Configure GOOGLE_API_KEY nos Settings > Repository secrets
# Para uso local: export GOOGLE_API_KEY="sua_chave_aqui"
# Obtenha em: https://makersuite.google.com/app/apikey

class ReviewResponseGenerator:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.model = None
        self.api_configured = False
        self.load_data()
        self.setup_model()
    
    def load_data(self):
        """Carrega o dataset de reviews"""
        try:
            self.df = pd.read_csv(self.csv_path)
            self.df = self.df.dropna(subset=["Review", "Liked"])
            self.df["Review"] = self.df["Review"].astype(str)
            self.df["Liked"] = self.df["Liked"].astype(int)
            print(f"✓ Dataset carregado: {self.df.shape[0]} avaliações")
        except Exception as e:
            print(f"✗ Erro ao carregar dataset: {e}")
            self.df = pd.DataFrame(columns=["Review", "Liked"])
    
    def setup_model(self):
        """Configura o modelo Gemini com tratamento robusto de API key"""
        # Tenta múltiplas fontes de API key (Spaces usa secrets)
        api_key = os.environ.get('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        if not api_key or api_key.strip() == "":
            print("⚠ GOOGLE_API_KEY não encontrada")
            print("  Para Hugging Face Spaces: Configure em Settings > Repository secrets")
            print("  Para uso local: export GOOGLE_API_KEY='sua_chave'")
            print("  Obtenha em: https://makersuite.google.com/app/apikey")
            self.api_configured = False
            return
        
        try:
            # Limpar a API key de espaços em branco
            api_key = api_key.strip()
            
            # Configurar com timeout e retry
            genai.configure(
                api_key=api_key,
                transport='rest'  # Usar REST ao invés de gRPC para melhor compatibilidade
            )
            
            # Tentar modelos em ordem de preferência
            model_names = [
                'gemini-2.0-flash-lite',
                'gemini-1.5-flash',
                'gemini-pro'
            ]
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    # Teste simples para verificar se o modelo funciona
                    test_response = self.model.generate_content("Hello")
                    if test_response:
                        print(f"✓ Modelo {model_name} configurado com sucesso")
                        self.api_configured = True
                        return
                except Exception as model_error:
                    print(f"✗ Tentativa com {model_name} falhou: {model_error}")
                    continue
            
            print("✗ Nenhum modelo disponível funcionou")
            self.api_configured = False
            
        except Exception as e:
            print(f"✗ Erro ao configurar API: {e}")
            self.api_configured = False
    
    def analisar_sentimento(self, review_text):
        """Analisa o sentimento da avaliação usando Gemini"""
        if not self.api_configured or not self.model:
            return "Erro", 3
        
        prompt = f"""Analise o sentimento desta avaliação de restaurante e retorne APENAS um número de 1 a 5:

Avaliação: "{review_text}"

Escala:
1 = Muito negativo
2 = Negativo
3 = Neutro
4 = Positivo
5 = Muito positivo

Responda APENAS com o número (1, 2, 3, 4 ou 5):"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=10
                )
            )
            stars = int(response.text.strip())
            
            # Validar resposta
            if stars < 1 or stars > 5:
                stars = 3
            
            # Classificar sentimento
            if stars >= 4:
                sentimento = "Positivo 😊"
            elif stars <= 2:
                sentimento = "Negativo 😕"
            else:
                sentimento = "Neutro 😐"
            
            return sentimento, stars
        except Exception as e:
            print(f"Erro na análise de sentimento: {e}")
            return "Neutro 😐", 3
    
    def gerar_resposta(self, review_text, stars):
        """Gera resposta personalizada usando Gemini"""
        if not self.api_configured or not self.model:
            return "❌ Modelo não configurado. Configure GOOGLE_API_KEY primeiro."
        
        # Definir contexto baseado no sentimento
        if stars >= 4:
            contexto = "agradecendo calorosamente e expressando satisfação"
            tom = "entusiasmado e grato"
        elif stars <= 2:
            contexto = "pedindo desculpas com empatia e oferecendo melhorias"
            tom = "empático e conciliador"
        else:
            contexto = "agradecendo cordialmente e valorizando o feedback"
            tom = "cordial e profissional"
        
        prompt = f"""Você é um atendente profissional de restaurante respondendo a uma avaliação de cliente.

Avaliação do cliente: "{review_text}"
Classificação: {stars} estrelas (de 1 a 5)

Instruções:
- Escreva uma resposta em português do Brasil
- Use tom {tom}
- Seja breve e direto (máximo 2-3 frases)
- {contexto}
- Use linguagem natural e profissional
- NÃO use emojis
- NÃO repita a avaliação do cliente
- Comece com "Olá" ou similar

Resposta do restaurante:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200
                )
            )
            resposta = response.text.strip()
            
            # Limpeza da resposta
            resposta = resposta.replace("Resposta do restaurante:", "").strip()
            resposta = resposta.replace("Resposta:", "").strip()
            
            # Garantir pontuação final
            if resposta and resposta[-1] not in ['.', '!', '?']:
                resposta += '.'
            
            # Fallback se resposta muito curta ou vazia
            if not resposta or len(resposta) < 15:
                if stars >= 4:
                    resposta = "Olá! Muito obrigado pelo feedback positivo! Ficamos felizes que gostou da experiência conosco."
                elif stars <= 2:
                    resposta = "Olá! Lamentamos pela experiência. Seu feedback é valioso para nossa melhoria contínua."
                else:
                    resposta = "Olá! Agradecemos seu comentário! Sua opinião nos ajuda a melhorar nossos serviços."
            
            return resposta
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return "Olá! Agradecemos seu feedback. Estamos sempre buscando melhorar nossos serviços."
    
    def processar_avaliacao(self, review_text):
        """Processa a avaliação completa: análise + resposta"""
        if not review_text.strip():
            return "Neutro 😐", "Por favor, insira uma avaliação."
        
        if not self.api_configured or not self.model:
            return "Erro 😞", "❌ API não configurada. Verifique se GOOGLE_API_KEY está configurada corretamente nos secrets do Spaces."
        
        try:
            # Análise de sentimento
            sentimento, stars = self.analisar_sentimento(review_text)
            
            # Geração de resposta
            resposta = self.gerar_resposta(review_text, stars)
            
            return f"{sentimento} ({stars} estrelas)", resposta
        except Exception as e:
            return "Erro 😞", f"Ocorreu um erro: {str(e)}"
    
    def exemplo_aleatorio(self):
        """Retorna uma avaliação aleatória do dataset"""
        if self.df is None or self.df.shape[0] == 0:
            return "A comida estava deliciosa e o atendimento foi excelente!"
        
        exemplo = self.df.sample(1).iloc[0]
        return exemplo["Review"]


# =====================================================
# 2. FUNÇÃO PARA CRIAR INTERFACE
# =====================================================
def create_interface():
    """Cria interface Gradio"""
    
    csv_path = "reviews_traduzidos.csv"
    generator = ReviewResponseGenerator(csv_path)
    
    # Verificar status da API
    api_status = "✓ API configurada" if generator.api_configured else "⚠ API não configurada"
    
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="emerald", secondary_hue="gray"), title="Food Review Reply AI") as app:
        # Cabeçalho
        gr.Markdown(f"""
        <div style="text-align: center;">
            <h1>🍽️ Food Review Reply AI - Gemini</h1>
            <p style="font-size: 16px; color: #666;">
                Sistema inteligente para gerar respostas automáticas e personalizadas para avaliações de clientes
            </p>
            <p style="font-size: 14px; color: #999;">
                Powered by Google Gemini (Gratuito)
            </p>
            <p style="font-size: 12px; color: {'green' if generator.api_configured else 'red'};">
                Status: {api_status}
            </p>
        </div>
        """)

        if not generator.api_configured:
            gr.Markdown("""
            <div style="margin: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                <strong>⚠️ Configuração necessária:</strong><br>
                Para Hugging Face Spaces: Configure <code>GOOGLE_API_KEY</code> em <strong>Settings > Repository secrets</strong><br>
                Para uso local: <code>export GOOGLE_API_KEY="sua_chave"</code><br>
                Obtenha sua chave em: <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a>
            </div>
            """)
        
        with gr.Row():
            review_input = gr.Textbox(
                label="Avaliação do cliente",
                placeholder="Ex: A comida estava deliciosa!",
                lines=3
            )
            btn_exemplo = gr.Button("📝 Exemplo aleatório")

        btn_exemplo.click(fn=generator.exemplo_aleatorio, outputs=review_input)
        btn_gerar = gr.Button("🤖 Gerar resposta", variant="primary")
        
        sentimento_output = gr.Label(label="Sentimento detectado")
        resposta_output = gr.Textbox(label="Resposta gerada", lines=3)

        btn_gerar.click(
            fn=generator.processar_avaliacao,
            inputs=review_input,
            outputs=[sentimento_output, resposta_output]
        )

        # Rodapé
        gr.Markdown("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #e0e0e0;">
            <p style="color: #888; font-size: 14px;">
                🚀 Desenvolvido com Gradio + Google Gemini • 
                👨‍🍳 Sistema de IA para atendimento ao cliente
            </p>
            <p style="color: #999; font-size: 12px;">
                API Key necessária: <a href="https://makersuite.google.com/app/apikey" target="_blank">Obtenha aqui</a>
            </p>
        </div>
        """)
    
    return app

# =====================================================
# 3. INICIALIZAÇÃO
# =====================================================
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
