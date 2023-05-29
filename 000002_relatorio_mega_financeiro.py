# API 000.003

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from utils import Database, tab
from datetime import datetime
import os


class Database(Database):
    def __init__(self): 
        super().__init__()
        self.columns = [
            'Filial', 'Tipo Agente', 'Agente', 'Tipo Doc', 'Fatura', 'Data Emissão', 'Data Entrada', 'Valor', 'Cond. Pagto', 'Nº Parc.', 'Série AP',
            'Parcela', 'Tipo Doc Parc.', 'Data Doc Parc.', 'Fatura Parc', 'Vencimento', 'Prorrogado', 'Valor Parc.', 'Red. Classe', 'Natureza',
            'Valor Classe', 'Red. C.Custo', 'Valor CC', 'Red. Projeto', 'Seq. CC', 'Seq. Proj', 'Valor Proj', 'Valor Rateio'
        ]

        self.columns_numbers = [
            "Valor", "Valor Parc.", "Valor Classe", "Valor CC", "Valor Proj", 'Valor Rateio'
        ]
    
    def relatorio_mega(self, coluna, ini, fim):
        sql = f"""
        SELECT 
            11000 + nf.filial AS "Filial", 
            'F' AS "Tipo Agente",
            COALESCE(cf.agente, 0) AS "Agente",
            'DESDIVS' AS "Tipo Doc",
            nf.documento AS "Fatura",    
            DATE_FORMAT(nf.emissao, '%d/%m/%Y') as "Data Emissão",
            DATE_FORMAT(CURDATE(), '%d/%m/%Y') as "Data Entrada",
            np.valor AS "Valor",
            'IMP' AS "Cond. Pagto",
            1 AS "Nº Parc.",
            'AP' AS "Série AP",
            '001' AS "Parcela",
            'DESDIVS' AS "Tipo Doc Parc.",
            DATE_FORMAT(CURDATE(), '%d/%m/%Y') as "Data Doc Parc.",
            nf.documento AS "Fatura Parc", 
            DATE_FORMAT(np.vencimento, '%d/%m/%Y') as "Vencimento",
            DATE_FORMAT(np.vencimento, '%d/%m/%Y') as "Prorrogado",
            np.valor AS "Valor Parc.",
            COALESCE(cf.red_classe, 0) AS "Red. Classe",
            'D' AS "Natureza",
            np.valor AS "Valor Classe",
            COALESCE(cc.extenso, cc.cc) AS "Red. C.Custo",
            np.valor AS "Valor CC",
            10111000 + nf.filial AS "Red. Projeto",
            '1' AS "Seq. CC",
            '1' AS "Seq. Proj",
            np.valor AS "Valor Proj",
            nr.valor AS "Valor Rateio"
        FROM nf_parcela np
        LEFT JOIN nf_nf nf ON np.nf_id = nf.id
        LEFT JOIN fornecedor_fornecedor cf ON nf.fornecedor_id = cf.id
        LEFT JOIN nf_rateio nr ON np.nf_id = nr.nf_id
        LEFT JOIN core_centrodecusto cc ON nr.cc_id = cc.id
        WHERE nf.tipo = 'D' AND {coluna} BETWEEN '{ini}' AND '{fim}'
        ORDER BY nf.filial;
        """
        #print(sql)
        return self.read_sql(sql)


try:
    db = Database()
    while True:
        tab()

        print('# # # # # RELATÓRIO IMPORTAÇÃO MEGA # # # # #\n')
        tab()
        
        print("""SELECIONE O TIPO DE RELATÓRIO:\n\n
        1. Atualizar Red Classe por CNPJ
        2. Atualizar Red Classe por Codigo Fornecedor (GPNF)
        3. Notas de Débito por Vencimento
        4. Notas de Débito por Emissão

    *** Caso não selecione nenhuma opção válida, será considerado o tipo de Relatório de Débito por Vencimento
        """)
        
        opcao = input('Digite a Opção desejada: ')
        
        
        if opcao in ('1', '2'):
            tab()
            print('Alteração de RED Classe')
            tab()
            if opcao == '1':
                cnpj = input('Digite o CNPJ: ')
                cnpj = cnpj.replace('.', '').replace('-', '').replace('/', '').replace(' ', '')
                red_classe = input('Digite a RED Classe: ')
                sql = f"UPDATE fornecedor_fornecedor SET red_classe = '{red_classe}' WHERE documento = '{cnpj}';"
                db.save_sql(sql)
                tab()
                print(f"RED Classe do CNPJ: {cnpj} alterado para {red_classe} com Sucesso!!!")
                tab()

            elif opcao == '2':
                id_fornecedor = input('Digite o Registro do Fornecedor (GPNF): ')
                id_fornecedor = id_fornecedor.replace('.', '').replace('-', '').replace('/', '').replace(' ', '').replace('#', '')
                red_classe = input('Digite a RED Classe: ')
                sql = f"UPDATE fornecedor_fornecedor SET red_classe = '{red_classe}' WHERE id = '{id_fornecedor}';"
                db.save_sql(sql)
                tab()
                print(f"RED Classe do Fornecedor com Registro: {id_fornecedor} alterado para {red_classe} com Sucesso!!!")
                tab()

        else:            
            if opcao == '4':
                coluna = 'nf.emissao'
                title = 'Relatório por Emissão'
            else:
                coluna = 'np.vencimento'
                title = 'Relatório por Vencimento'

                    
            ini = input('Digite a data INICAIL [Formato: dd/mm/aaaa]: ')
            fim = input('Digite a data FINAL [Formato: dd/mm/aaaa]: ')

            hoje = datetime.now()
            if ini == '':
                ini = datetime(hoje.year, hoje.month, 1).strftime('%d/%m/%Y')
            
            if fim == '':
                fim = hoje.strftime('%d/%m/%Y')

            #ini = '01/04/2023'
            #fim = '30/04/2023'

            tab()

            hoje = hoje.strftime('%Y%m%d%H%M%S') 
            
            print(f'Gerando {title} referente à {ini} à {fim}...')
            ini = ini.split('/')
            ini = f"{ini[-1]}-{ini[-2]}-{ini[-3]}"
            fim = fim.split('/')
            fim = f"{fim[-1]}-{fim[-2]}-{fim[-3]}"
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                        
            df = db.relatorio_mega(coluna, ini, fim)

            qtde = df[['Filial','Fatura', 'Agente', 'Data Emissão', 'Tipo Agente']].groupby(['Filial', 'Fatura', 'Agente', 'Data Emissão'], as_index=False).count()
            qtde.rename(columns={'Tipo Agente': 'qtde'}, inplace=True)

            df = df.merge(qtde, on=['Filial','Fatura', 'Agente', 'Data Emissão'], how='left')            
            df_rateio = df[df.qtde > 1]
            df = df[df.qtde == 1]

            del df['qtde']
            del df['Valor Rateio']
            df = df.drop_duplicates()

            if len(df) > 0:
                df_name = f"{desktop_path}/{title} - {ini} à {fim} ({hoje}).xlsx"
                print(f'Salvando Arquivo em: {df_name}')
                df.to_excel(df_name, index=False)

            if len(df_rateio) > 0:
                df_rateio.rename(columns={'qtde': 'Qtde Rateio'}, inplace=True)
                df_name = f"{desktop_path}/{title} - Documentos com Rateio - {ini} à {fim} ({hoje}).xlsx"
                print(f'Salvando Arquivo em: {df_name}')
                df_rateio.to_excel(df_name, index=False)
            
            

        tab()
        opcao_continuar = input('Digite 0 e pressione enter pra sair ou apenas enter para Gerar outro Relatório: ')        
        if opcao_continuar == '0':
            break
    
    

except Exception as error:    
    tab()
    for e in error.args:
        print(e)
        tab()

    input('Pressione ENTER para Sair')


#input('Pressione Enter para sair')


"""
RELATÓRIO DE VERSÃO

2023-05-15
    Criado Relatório conforme solicitação do Financeiro

2023-05-18
    Alterado CC para trazer o Extenso, conforme solicitação do Financeiro
    Se não existir o Extenso cadastrado irá trazer o CC (Reduzido)

"""