import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Análise Campeonato Brasileiro", page_icon="⚽", layout="wide")

st.title("⚽ Análise do Campeonato Brasileiro (2003-2022)")
st.markdown("---")

# URLs dos arquivos CSV no GitHub (raw)
urls = {
    'full': 'https://raw.githubusercontent.com/vconceicao/ada_brasileirao_dataset/master/campeonato-brasileiro-full.csv',
    'gols': 'https://raw.githubusercontent.com/vconceicao/ada_brasileirao_dataset/master/campeonato-brasileiro-gols.csv',
    'cartoes': 'https://raw.githubusercontent.com/vconceicao/ada_brasileirao_dataset/master/campeonato-brasileiro-cartoes.csv',
    'estatisticas': 'https://raw.githubusercontent.com/vconceicao/ada_brasileirao_dataset/master/campeonato-brasileiro-estatisticas-full.csv'
}

@st.cache_data
def load_data():
    """Carrega todos os arquivos CSV"""
    with st.spinner('Carregando dados...'):
        try:
            df_full = pd.read_csv(urls['full'], encoding='utf-8')
            df_gols = pd.read_csv(urls['gols'], encoding='utf-8')
            df_cartoes = pd.read_csv(urls['cartoes'], encoding='utf-8')
            df_estatisticas = pd.read_csv(urls['estatisticas'], encoding='utf-8')
            
            # Converter coluna de data para datetime e extrair o ano
            if 'data' in df_full.columns:
                df_full['data_dt'] = pd.to_datetime(df_full['data'], format='%d/%m/%Y', errors='coerce')
                df_full['ano'] = df_full['data_dt'].dt.year
            
            if 'data' in df_gols.columns:
                df_gols['data_dt'] = pd.to_datetime(df_gols['data'], format='%d/%m/%Y', errors='coerce')
                df_gols['ano'] = df_gols['data_dt'].dt.year
            
            if 'data' in df_cartoes.columns:
                df_cartoes['data_dt'] = pd.to_datetime(df_cartoes['data'], format='%d/%m/%Y', errors='coerce')
                df_cartoes['ano'] = df_cartoes['data_dt'].dt.year
            
            return df_full, df_gols, df_cartoes, df_estatisticas
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return None, None, None, None

# Carregar dados
df_full, df_gols, df_cartoes, df_estatisticas = load_data()

if df_full is not None:
    
    # Debug: Mostrar colunas disponíveis (pode ser removido depois)
    with st.expander("🔍 Ver estrutura dos dados (Debug)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Colunas - Jogos:**")
            st.write(df_full.columns.tolist())
        with col2:
            st.write("**Colunas - Gols:**")
            st.write(df_gols.columns.tolist())
        with col3:
            st.write("**Colunas - Cartões:**")
            st.write(df_cartoes.columns.tolist())
    
    # Criar tabs para organizar as análises
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🏆 Time Vencedor 2008",
        "🗺️ Estado com Menos Jogos",
        "⚽ Artilheiro Geral",
        "🎯 Artilheiro de Pênaltis",
        "🔄 Gols Contra",
        "🟨 Cartões Amarelos",
        "🟥 Cartões Vermelhos",
        "🎲 Partida com Mais Gols"
    ])
    
    # TAB 1: Time que mais venceu em 2008
    with tab1:
        st.header("🏆 Time que mais venceu jogos em 2008")
        
        try:
            # Filtrar jogos de 2008
            df_2008 = df_full[df_full['ano'] == 2008].copy()
            
            if len(df_2008) == 0:
                st.warning("Não foram encontrados jogos de 2008 nos dados.")
            else:
                # Contar vitórias por time
                vitorias = df_2008['vencedor'].value_counts()
                
                # Remover valores nulos ou '-' que indicam empate
                vitorias = vitorias[vitorias.index.notna()]
                vitorias = vitorias[vitorias.index != '-']
                
                if len(vitorias) > 0:
                    time_campeao = vitorias.index[0]
                    num_vitorias = vitorias.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Time com mais vitórias", time_campeao, f"{num_vitorias} vitórias")
                        
                        st.subheader("Top 10 times com mais vitórias em 2008")
                        top10 = vitorias.head(10).reset_index()
                        top10.columns = ['Time', 'Vitórias']
                        st.dataframe(top10, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(vitorias.head(10), 
                                   title='Top 10 Times - Vitórias em 2008',
                                   labels={'value': 'Número de Vitórias', 'index': 'Time'},
                                   color=vitorias.head(10).values,
                                   color_continuous_scale='Greens')
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar dados de 2008: {str(e)}")
    
    # TAB 2: Estado com menos jogos
    with tab2:
        st.header("🗺️ Estado com menos jogos (2003-2022)")
        
        try:
            # Filtrar período
            df_periodo = df_full[(df_full['ano'] >= 2003) & (df_full['ano'] <= 2022)].copy()
            
            # Contar jogos por estado (mandante e visitante)
            jogos_mandante = df_periodo['mandante_Estado'].value_counts()
            jogos_visitante = df_periodo['visitante_Estado'].value_counts()
            
            # Somar jogos como mandante e visitante
            total_jogos = jogos_mandante.add(jogos_visitante, fill_value=0).sort_values()
            
            if len(total_jogos) > 0:
                estado_menos_jogos = total_jogos.index[0]
                num_jogos = int(total_jogos.values[0])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Estado com menos jogos", estado_menos_jogos, f"{num_jogos} jogos")
                    
                    st.subheader("Estados com menos jogos")
                    bottom10 = total_jogos.head(10).reset_index()
                    bottom10.columns = ['Estado', 'Número de Jogos']
                    st.dataframe(bottom10, use_container_width=True)
                
                with col2:
                    fig = px.bar(total_jogos.head(10), 
                               title='10 Estados com Menos Jogos (2003-2022)',
                               labels={'value': 'Número de Jogos', 'index': 'Estado'},
                               color=total_jogos.head(10).values,
                               color_continuous_scale='Reds_r')
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar dados de estados: {str(e)}")
    
    # TAB 3: Jogador com mais gols
    with tab3:
        st.header("⚽ Artilheiro Geral")
        
        try:
            # Verificar se a coluna 'atleta' existe
            if 'atleta' in df_gols.columns:
                artilheiros = df_gols['atleta'].value_counts()
                
                # Remover valores nulos
                artilheiros = artilheiros[artilheiros.index.notna()]
                
                if len(artilheiros) > 0:
                    artilheiro = artilheiros.index[0]
                    num_gols = artilheiros.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Artilheiro Geral", artilheiro, f"{num_gols} gols")
                        
                        st.subheader("Top 20 Artilheiros")
                        top20 = artilheiros.head(20).reset_index()
                        top20.columns = ['Jogador', 'Gols']
                        st.dataframe(top20, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(artilheiros.head(15), 
                                   title='Top 15 Artilheiros',
                                   labels={'value': 'Gols', 'index': 'Jogador'},
                                   color=artilheiros.head(15).values,
                                   color_continuous_scale='Blues')
                        fig.update_xaxis(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Coluna 'atleta' não encontrada no dataset de gols.")
        except Exception as e:
            st.error(f"Erro ao processar artilheiros: {str(e)}")
    
    # TAB 4: Jogador com mais gols de pênalti
    with tab4:
        st.header("🎯 Artilheiro de Pênaltis")
        
        try:
            # Verificar se as colunas existem
            if 'atleta' in df_gols.columns and 'tipo_de_gol' in df_gols.columns:
                # Filtrar apenas gols de pênalti
                penaltis = df_gols[df_gols['tipo_de_gol'].str.contains('Penalty|Pênalti|Penalti', case=False, na=False)]
                artilheiros_penalti = penaltis['atleta'].value_counts()
                
                # Remover valores nulos
                artilheiros_penalti = artilheiros_penalti[artilheiros_penalti.index.notna()]
                
                if len(artilheiros_penalti) > 0:
                    artilheiro_penalti = artilheiros_penalti.index[0]
                    num_penaltis = artilheiros_penalti.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Maior cobrador de pênaltis", artilheiro_penalti, f"{num_penaltis} gols")
                        
                        st.subheader("Top 15 Cobradores de Pênaltis")
                        top15_pen = artilheiros_penalti.head(15).reset_index()
                        top15_pen.columns = ['Jogador', 'Pênaltis Convertidos']
                        st.dataframe(top15_pen, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(artilheiros_penalti.head(15), 
                                   title='Top 15 Cobradores de Pênaltis',
                                   labels={'value': 'Pênaltis', 'index': 'Jogador'},
                                   color=artilheiros_penalti.head(15).values,
                                   color_continuous_scale='Purples')
                        fig.update_xaxis(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foram encontrados gols de pênalti nos dados.")
            else:
                st.warning("Colunas necessárias não encontradas no dataset de gols.")
        except Exception as e:
            st.error(f"Erro ao processar pênaltis: {str(e)}")
    
    # TAB 5: Jogador com mais gols contra
    with tab5:
        st.header("🔄 Gols Contra")
        
        try:
            if 'atleta' in df_gols.columns and 'tipo_de_gol' in df_gols.columns:
                # Filtrar apenas gols contra
                gols_contra = df_gols[df_gols['tipo_de_gol'].str.contains('Gol Contra|Contra|Own Goal', case=False, na=False)]
                jogadores_gols_contra = gols_contra['atleta'].value_counts()
                
                # Remover valores nulos
                jogadores_gols_contra = jogadores_gols_contra[jogadores_gols_contra.index.notna()]
                
                if len(jogadores_gols_contra) > 0:
                    jogador_mais_gc = jogadores_gols_contra.index[0]
                    num_gc = jogadores_gols_contra.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Jogador com mais gols contra", jogador_mais_gc, f"{num_gc} gols contra")
                        
                        st.subheader("Top 15 Jogadores com Gols Contra")
                        top15_gc = jogadores_gols_contra.head(15).reset_index()
                        top15_gc.columns = ['Jogador', 'Gols Contra']
                        st.dataframe(top15_gc, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(jogadores_gols_contra.head(15), 
                                   title='Top 15 Jogadores com Gols Contra',
                                   labels={'value': 'Gols Contra', 'index': 'Jogador'},
                                   color=jogadores_gols_contra.head(15).values,
                                   color_continuous_scale='Oranges')
                        fig.update_xaxis(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foram encontrados gols contra nos dados.")
            else:
                st.warning("Colunas necessárias não encontradas no dataset de gols.")
        except Exception as e:
            st.error(f"Erro ao processar gols contra: {str(e)}")
    
    # TAB 6: Jogador com mais cartões amarelos
    with tab6:
        st.header("🟨 Cartões Amarelos")
        
        try:
            if 'atleta' in df_cartoes.columns and 'cartao' in df_cartoes.columns:
                # Filtrar cartões amarelos
                cartoes_amarelos = df_cartoes[df_cartoes['cartao'] == 'Amarelo']
                jogadores_amarelos = cartoes_amarelos['atleta'].value_counts()
                
                # Remover valores nulos
                jogadores_amarelos = jogadores_amarelos[jogadores_amarelos.index.notna()]
                
                if len(jogadores_amarelos) > 0:
                    jogador_mais_amarelos = jogadores_amarelos.index[0]
                    num_amarelos = jogadores_amarelos.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Jogador com mais cartões amarelos", jogador_mais_amarelos, f"{num_amarelos} cartões")
                        
                        st.subheader("Top 20 Jogadores - Cartões Amarelos")
                        top20_am = jogadores_amarelos.head(20).reset_index()
                        top20_am.columns = ['Jogador', 'Cartões Amarelos']
                        st.dataframe(top20_am, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(jogadores_amarelos.head(15), 
                                   title='Top 15 - Cartões Amarelos',
                                   labels={'value': 'Cartões Amarelos', 'index': 'Jogador'},
                                   color=jogadores_amarelos.head(15).values,
                                   color_continuous_scale='YlOrBr')
                        fig.update_xaxis(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foram encontrados cartões amarelos nos dados.")
            else:
                st.warning("Colunas necessárias não encontradas no dataset de cartões.")
        except Exception as e:
            st.error(f"Erro ao processar cartões amarelos: {str(e)}")
    
    # TAB 7: Jogador com mais cartões vermelhos
    with tab7:
        st.header("🟥 Cartões Vermelhos")
        
        try:
            if 'atleta' in df_cartoes.columns and 'cartao' in df_cartoes.columns:
                # Filtrar cartões vermelhos
                cartoes_vermelhos = df_cartoes[df_cartoes['cartao'] == 'Vermelho']
                jogadores_vermelhos = cartoes_vermelhos['atleta'].value_counts()
                
                # Remover valores nulos
                jogadores_vermelhos = jogadores_vermelhos[jogadores_vermelhos.index.notna()]
                
                if len(jogadores_vermelhos) > 0:
                    jogador_mais_vermelhos = jogadores_vermelhos.index[0]
                    num_vermelhos = jogadores_vermelhos.values[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Jogador com mais cartões vermelhos", jogador_mais_vermelhos, f"{num_vermelhos} cartões")
                        
                        st.subheader("Top 20 Jogadores - Cartões Vermelhos")
                        top20_vm = jogadores_vermelhos.head(20).reset_index()
                        top20_vm.columns = ['Jogador', 'Cartões Vermelhos']
                        st.dataframe(top20_vm, use_container_width=True)
                    
                    with col2:
                        fig = px.bar(jogadores_vermelhos.head(15), 
                                   title='Top 15 - Cartões Vermelhos',
                                   labels={'value': 'Cartões Vermelhos', 'index': 'Jogador'},
                                   color=jogadores_vermelhos.head(15).values,
                                   color_continuous_scale='Reds')
                        fig.update_xaxis(tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Não foram encontrados cartões vermelhos nos dados.")
            else:
                st.warning("Colunas necessárias não encontradas no dataset de cartões.")
        except Exception as e:
            st.error(f"Erro ao processar cartões vermelhos: {str(e)}")
    
    # TAB 8: Partida com mais gols
    with tab8:
        st.header("🎲 Partida com Mais Gols")
        
        try:
            # Calcular total de gols por partida
            df_full['total_gols'] = df_full['mandante_Placar'] + df_full['visitante_Placar']
            
            # Encontrar partida com mais gols
            partida_mais_gols = df_full.loc[df_full['total_gols'].idxmax()]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🏟️ Partida com maior número de gols")
                
                # Criar um placar visual
                placar_html = f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 30px; 
                            border-radius: 15px; 
                            text-align: center;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                    <h2 style="color: white; margin: 0; font-size: 24px;">{partida_mais_gols['mandante']}</h2>
                    <h1 style="color: #FFD700; margin: 20px 0; font-size: 48px; font-weight: bold;">
                        {int(partida_mais_gols['mandante_Placar'])} x {int(partida_mais_gols['visitante_Placar'])}
                    </h1>
                    <h2 style="color: white; margin: 0; font-size: 24px;">{partida_mais_gols['visitante']}</h2>
                    <p style="color: #f0f0f0; margin-top: 20px; font-size: 18px;">
                        📅 {partida_mais_gols['data']} | 🏆 Rodada {int(partida_mais_gols['rodata'])}
                    </p>
                    <p style="color: #FFD700; margin-top: 10px; font-size: 22px; font-weight: bold;">
                        ⚽ Total: {int(partida_mais_gols['total_gols'])} gols
                    </p>
                </div>
                """
                st.markdown(placar_html, unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader("Detalhes da partida")
                
                detalhes = {
                    'Informação': ['Mandante', 'Visitante', 'Placar', 'Data', 'Rodada', 'Arena', 'Vencedor', 'Total de Gols'],
                    'Valor': [
                        partida_mais_gols['mandante'],
                        partida_mais_gols['visitante'],
                        f"{int(partida_mais_gols['mandante_Placar'])} x {int(partida_mais_gols['visitante_Placar'])}",
                        partida_mais_gols['data'],
                        int(partida_mais_gols['rodata']),
                        partida_mais_gols['arena'],
                        partida_mais_gols['vencedor'],
                        int(partida_mais_gols['total_gols'])
                    ]
                }
                
                df_detalhes = pd.DataFrame(detalhes)
                st.dataframe(df_detalhes, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📊 Top 10 Partidas")
                top10_gols = df_full.nlargest(10, 'total_gols')[['mandante', 'visitante', 'mandante_Placar', 'visitante_Placar', 'total_gols', 'data']].copy()
                top10_gols['Placar'] = top10_gols['mandante_Placar'].astype(int).astype(str) + ' x ' + top10_gols['visitante_Placar'].astype(int).astype(str)
                top10_gols['Jogo'] = top10_gols['mandante'] + ' vs ' + top10_gols['visitante']
                
                display_df = top10_gols[['Jogo', 'Placar', 'total_gols']].copy()
                display_df.columns = ['Partida', 'Placar', 'Total']
                display_df = display_df.reset_index(drop=True)
                display_df.index = display_df.index + 1
                
                st.dataframe(display_df, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar partidas: {str(e)}")
    
    # Sidebar com informações gerais
    with st.sidebar:
        st.header("📊 Informações Gerais")
        st.metric("Total de Jogos", len(df_full))
        st.metric("Total de Gols", len(df_gols))
        st.metric("Total de Cartões", len(df_cartoes))
        st.metric("Período", "2003-2022")
        
        st.markdown("---")
        st.markdown("### 📁 Datasets Carregados")
        st.success("✅ Campeonato Full")
        st.success("✅ Gols")
        st.success("✅ Cartões")
        st.success("✅ Estatísticas")
        
        st.markdown("---")
        st.markdown("#### 💡 Sobre")
        st.info("Análise completa dos dados do Campeonato Brasileiro entre 2003 e 2022.")

else:
    st.error("❌ Não foi possível carregar os dados. Verifique a conexão com o repositório GitHub.")