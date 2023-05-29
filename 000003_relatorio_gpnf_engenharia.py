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
            'Conta Contábil', 'Filial', 'Fornecedor', 'Data Emissão', 'Documento', 'Finalidade', 'Vencimento', 'Valor Parcela'
        ]

        self.columns_numbers = [
            'Valor Parcela'
        ]
    
    def relatorio(self, conta, ini, fim):
        sql = f"""
        SELECT 
            ct.descricao AS "Conta Contábil",
            nf.filial AS "Filial", 
            cf.nome AS "Fornecedor",
            DATE_FORMAT(nf.emissao, '%d/%m/%Y') as "Data Emissão",
            nf.documento AS "Documento", 
            nf.finalidade AS "Finalidade", 
            DATE_FORMAT(np.vencimento, '%d/%m/%Y') as "Vencimento",
            np.valor AS "Valor Parcela"
        FROM nf_parcela np
        LEFT JOIN nf_nf nf ON np.nf_id = nf.id
        LEFT JOIN core_contacontabil ct ON nf.conta_id = ct.id
        LEFT JOIN fornecedor_fornecedor cf ON nf.fornecedor_id = cf.id
        LEFT JOIN nf_rateio nr ON np.nf_id = nr.nf_id
        LEFT JOIN core_centrodecusto cc ON nr.cc_id = cc.id
        WHERE ct.conta {conta} AND  nf.emissao BETWEEN '{ini}' AND '{fim}'
        ORDER BY nf.filial;
        """
        #print(sql)
        return self.read_sql(sql)


try:
    db = Database()
    while True:
        tab()

        print('# # # # # RELATÓRIO NOTAS FISCAIS # # # # #\n')
        tab()
        
        print("""SELECIONE O TIPO DE RELATÓRIO:\n\n
        1. Relatório Contas 643 e 644
        2. Relatório Conta 643
        3. Relatório Conta 644

        *** Caso não selecione nenhuma opção válida seja selecionada, será considerado o tipo de Relatório Contas 643 e 644
        """)
        
        opcao = input('Digite a Opção desejada: ')
        
        conta = 'in (643, 644)'
        title = 'Relatório Contas 643 e 644'

        if opcao in '2':
           conta = '= 643'
           title = 'Relatório Conta 643'
        elif opcao == '3':
            conta = '= 644'
            title = 'Relatório Conta 644'


        if True:

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
                        
            df = db.relatorio(conta, ini, fim)

            if len(df) > 0:
                df_name = f"{desktop_path}/{title} - {ini} à {fim} ({hoje}).xlsx"
                print(f'Salvando Arquivo em: {df_name}')
                df.to_excel(df_name, index=False)
            
            

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

2023-05-29
    Criado Relatório conforme solicitação do Engenharia

"""