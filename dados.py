import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar o arquivo Excel
arquivo = "Check-list de Verificação Botafogo.xlsx"
df = pd.read_excel(arquivo)

def relatorios():
    # Renomear 'sim' e 'não' para 'Exportado' e 'Não Exportado'
    df["Relatório Exportado"].replace({"sim": "Enviados", "não": "Não Enviados"}, inplace=True)
    # Contar as ocorrências de cada valor na coluna 'Relatório Exportado'
    contagem = df["Relatório Exportado"].value_counts()
    # Criar um DataFrame com os dados
    data = pd.DataFrame({'Categoria': contagem.index, 'Quantidade': contagem.values})
    # Criar o gráfico de pizza com Plotly Express
    fig = px.pie(data, values='Quantidade', names='Categoria', title='Status de envios dos Relatórios', hole=0.5)
    return fig

def acompanhamento():
    # Calcular a contagem de ocorrências por data
    contagem_datas = df["Data"].value_counts().reset_index()
    contagem_datas.columns = ["Data", "Quantidade"]

    # Ordenar as datas para garantir que o gráfico esteja em ordem cronológica
    contagem_datas = contagem_datas.sort_values(by="Data")

    # Criar o gráfico de barras com Plotly Express
    fig = px.bar(contagem_datas, x='Data', y='Quantidade', title='Quantidade de Validações por Data', 
                category_orders={"Data": contagem_datas["Data"]})  # Define a ordem das categorias
    fig.update_xaxes(title_text='Data', tickangle=45)
    fig.update_yaxes(title_text='Quantidade de Validaçoes')
    
    return fig

def pontos():
    pontos_totais = 236
    pontos_validados = df["Data"].count()
    
    # Criar um DataFrame com os dados
    data = {'Categoria': ['Pontos Totais', 'Pontos Validados'],
            'Pontos': [pontos_totais, pontos_validados],
            'Status': ['Totais', 'Validados']}
    df_pontos = pd.DataFrame(data)
    
    # Mapear cores para os status
    cor = {'Totais': '#4F4F4F', 'Validados': '#000080'}
    
    # Criar o gráfico de barras com Plotly Express
    fig = px.bar(df_pontos, x='Categoria', y='Pontos', color='Status',
                 title='Pontos Totais x Pontos Validados', 
                 labels={'Pontos': 'Pontos', 'Categoria': 'Categoria'},
                 color_discrete_map=cor)
    
    return fig

# Criação do cabeçalho com logo
st.set_page_config(page_title="Dashboard Botafogo", page_icon=":chart_with_upwards_trend:")
st.title("Dashboard de Verificação Botafogo")

# Adiciona logo
st.image("logo_botafogo.png", width=200)

# Gráfico de pizza para o status dos relatórios
st.header("Status de Envios dos Relatórios")
fig_relatorios = relatorios()
st.plotly_chart(fig_relatorios, use_container_width=True)

# Gráfico de barras para o acompanhamento das datas
st.header("Acompanhamento de Validações por Data")
fig_acompanhamento = acompanhamento()
st.plotly_chart(fig_acompanhamento, use_container_width=True)

# Gráfico de barras para os pontos
st.header("Pontos Totais vs. Pontos Validados")
fig_pontos = pontos()
st.plotly_chart(fig_pontos, use_container_width=True)

# Estatísticas
st.header("Estatísticas")
media_datas = df["Data"].value_counts().mean()
pontos_totais = 236
pontos_validados = df['Data'].count()
relatorios = df['Relatório Exportado'].value_counts()
st.write("Média de Validações por Data:", media_datas)
st.write("Pontos Totais:", pontos_totais)
st.write("Pontos Validados:", pontos_validados)
st.write("Status de Envios dos Relatórios:")
st.write(relatorios)
