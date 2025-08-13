import streamlit as st
import pandas as pd
from APIGoogleSheets import GoogleSheets

# Configura o título da página
st.set_page_config(
         page_title="Agenda",
         page_icon="images.png",
         layout="wide",
     )

@st.cache_data
def add_activity(df, local, atividade, data, horario):
    new_data = {'Local': [local], 'Atividade': [atividade], 'Data': [data], 'Horário': [horario]}
    new_df = pd.DataFrame(new_data)
    df = pd.concat([df, new_df], ignore_index=True)
    return df
@st.cache_data
# Função para reagendar uma atividade existente
def reschedule_activity(df, index, new_date, new_time):
    df.at[index, 'Data'] = new_date
    df.at[index, 'Horário'] = new_time
    return df

@st.cache_data
# Função para visualizar as atividades de um dia específico
def view_activities_dia(df, search_date):
    search_date_str = search_date.strftime('%d/%m/%Y')
    filtered_df = df[df["Data"].dt.strftime('%d/%m/%Y') == search_date_str]

    if filtered_df.empty:
        st.warning("Não há atividades para a data selecionada.")
    else:
        st.subheader(f"Atividades - {search_date_str}")
        # Convert 'Horário' column to datetime objects
        filtered_df['Horário'] = pd.to_datetime(filtered_df['Horário'])
        # Sort DataFrame by 'Horário' column
        filtered_df = filtered_df.sort_values(by='Horário')
        # Convert 'Horário' column back to string for display
        filtered_df['Horário'] = filtered_df['Horário'].dt.strftime('%H:%M:%S')

        return filtered_df

def main():
    
    planilha = GoogleSheets()
    df_planilha = planilha.fetch_values()
    # Carregar os dados do Google Sheets
    df = df_planilha

    # Define as opções do menu na barra lateral
    opcoes_shopp = st.sidebar.selectbox("Shopping", ["Botafogo", "Itaquera"])
    
    st.title(f"Agenda de atividades {opcoes_shopp}")
    
    if opcoes_shopp == "Botafogo":
   
        # Define as opções do menu na barra lateral
        opcao = st.sidebar.radio("Opções", ["Visualizar Atividades", "Adicionar Atividade", "Editar/Reagendar Atividade", "Excluir Atividades"])
        if opcao == "Visualizar Atividades":
            # Opção para pesquisar por data ou por local
            tipo_pesquisa = st.radio("Filtro da Pesquisa:", ["Data", "Local"])
            
            if tipo_pesquisa == "Data":
                # Pesquisar por um dia específico
                search_date = st.date_input("Selecione uma data:")
                visualizar_sheets = view_activities_dia(df, search_date)  # Passando a data de pesquisa como argumento

                if visualizar_sheets is not None:
                    st.table(visualizar_sheets) 
                    
                    if not visualizar_sheets.empty:
                        selected_local = st.selectbox("Selecione o local:", visualizar_sheets["Local"].unique()) 

                        expander = st.expander("Informações")
                        filtered_sheets = visualizar_sheets[visualizar_sheets["Local"] == selected_local]
                        if not filtered_sheets.empty:
                            # Exibir os dados como um formulário dentro do expander
                            with expander:
                                for index, row in filtered_sheets.iterrows():
                                    data_formatada = row['Data'].strftime('%Y-%m-%d')
                                    st.write(f"Atividade: {row['Atividade']}")
                                    st.write(f"Status: {row['Status']}")
                                    st.write(f"Data: {data_formatada}")
                                    st.write(f"Hora: {row['Horário']}")
                        else:
                            expander.warning(f"Não há atividades para o local '{selected_local}' na data selecionada.")
                    else:
                        st.warning("Não há atividades para a data selecionada.")
                else:
                    pass
                            
            if tipo_pesquisa == "Local":
                st.subheader("Pesquisar por Local")
                selected_local = st.selectbox("Selecione o local:", df["Local"].unique())
                visualizar_sheets = df[df["Local"] == selected_local]
                st.table(visualizar_sheets)
            
            
                if visualizar_sheets is not None:
                    expander = st.expander("Informações")

                    if not visualizar_sheets.empty:
                        # Exibir os dados como um formulário dentro do expander
                        with expander:
                            
                            for index, row in visualizar_sheets.iterrows():
                                data_formatada = row['Data'].strftime('%Y-%m-%d')
                                st.write(f"Atividade: {row['Atividade']}")
                                st.write(f"Status: {row['Status']}")
                                st.write(f"Data: {data_formatada}")
                                st.write(f"Hora: {row['Horário']}")
                                
                    else:
                        expander.warning("Não há atividades para o local ou data selecionado.")
            
        elif opcao == "Adicionar Atividade":
            st.subheader("Adicionar Atividade")
            local = st.text_input("Local:")
            atividade = st.text_input("Atividade:")
            data = st.date_input("Data:")
            horario = st.time_input("Horário:")
            if st.button("Adicionar"):
                # Convert date to string before passing to add_values()
                str_data = data.strftime('%Y-%m-%d')
                str_horario = horario.strftime('%H:%M:%S')
                planilha.add_values(local, atividade, "",str_data, str_horario)
                
                st.success("Atividade adicionada com sucesso!")

        elif opcao == "Editar/Reagendar Atividade":
            st.subheader("Reagendar Atividade")
            search_date = st.date_input("Selecione uma data:")
            visualizar_sheets = view_activities_dia(df, search_date)  # Passando a data de pesquisa como argumento
            st.table(visualizar_sheets) 
            
            # Selecionar o local da atividade para reagendar
            locais = df[df["Data"].dt.strftime('%d/%m/%Y') == search_date.strftime('%d/%m/%Y')]["Local"].unique()
            local_selecionado = st.selectbox("Selecione o local da atividade para reagendar:", locais)

            
            # Reagendar a atividade selecionada
            new_date = st.date_input("Nova Data:", value=search_date)
            new_time = st.time_input("Novo Horário:")
            realizado = st.text_input("Foi realizado?")

            # Convert new_date and new_time to appropriate formats
            str_new_date = new_date.strftime('%Y-%m-%d')
            str_new_time = new_time.strftime('%H:%M:%S')

            # Filtrar o DataFrame para encontrar a linha correspondente ao local selecionado
            atividade_para_reagendar = df[(df["Data"].dt.strftime('%d/%m/%Y') == search_date.strftime('%d/%m/%Y')) & (df["Local"] == local_selecionado)]
            if st.button("Salvar reagendamento !"):
                # Verificar se há uma atividade para reagendar
                if not atividade_para_reagendar.empty:
                
                    # Add rescheduled activity using the add_values method
                    planilha.update_values(local=local_selecionado, atividade=atividade_para_reagendar['Atividade'].iloc[0],realizado=realizado ,data=str_new_date, horario=str_new_time)
                    
                    st.success("Atividade reagendada com sucesso!")
                else:
                    st.warning("Não há atividade para reagendar neste local e data.")
        
        if opcao == "Excluir Atividades":
            st.subheader("Excluir Atividades")

            # Pedir senha para confirmar a exclusão
            senha = st.text_input("Digite a senha para confirmar a exclusão:", type="password")

            if senha == "1234":  # Substitua "sua_senha" pela senha real
                # Permitir ao usuário escolher uma atividade para excluir
                selected_activity = st.selectbox("Selecione a atividade para excluir:", df["Local"])

                # Obtém o índice da linha para a atividade selecionada
                row_index = df.index[df["Local"] == selected_activity].tolist()[0]

                if st.button("Excluir"):
                    planilha.delete_row(row_index)
                    st.success("Local excluída com sucesso!")
            else:
                st.warning("Senha incorreta. Por favor, tente novamente.")

    elif opcoes_shopp == "Itaquera":
        st.write("Em produção...")


if __name__ == '__main__':
    main()