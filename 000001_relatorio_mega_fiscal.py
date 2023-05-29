# API 000.001

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from local_settings import host, port, user, password, database

import mysql.connector
import pandas as pd
from datetime import datetime
import os


class Database:
    def __init__(self): 
        self.columns = [
            "Filial", "Ação", "NF", "Série", "Data de Emissão", "Data Entrada", "Agente", "Cond. Pag.", "Tipo de Preço",
            "Total Merc.", "Total Descto", "Total Acresc.", "Total Nota", "CC. Padrão", "Proj. Padrão", "Seq. Item",
            "Cód Item", "Quant. Item", "Vlr Unit.Item", "Descto", "Acrescimo", "Total Item", "CST ICMS", "APL.",
            "Nº DOC.", "Parcela", "Venc.", "Valor Parcela", "ORG.", "C.C.", "Proj. Padrão"
        ]

        self.columns_numbers = [
            "Total Merc.", "Total Descto", "Total Acresc.", "Total Nota", "Vlr Unit.Item", "Descto", "Acrescimo", "Total Item", "Valor Parcela"
        ]

    def read_sql(self, sql):
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        df = pd.read_sql(sql, conn)

        #df.columns = self.columns

        for c in self.columns_numbers:
            df[c] = df[c].map(lambda x: f"{x:,.2f}".replace('.', '||').replace(',', '.').replace('||', ','))

        return df
    
    def relatorio_mega(self, ini, fim, where, item, serie):
        sql = f"""
        select
            (nf.filial + 11000) as "Filial",
            59 as "Ação",
            nf.documento as "NF",
            '{serie}' as "Série",
            date_format(nf.emissao, '%d/%m/%Y') as "Data de Emissão",
            DATE_FORMAT(CURDATE(), '%d/%m/%Y') as "Data Entrada",
            f.agente as "Agente",
            0 as "Cond. Pag.",
            'SEM' as "Tipo de Preço",
            p.valor as "Total Merc.",
            0 as "Total Descto",
            0 as "Total Acresc.",
            p.valor as "Total Nota",
            cc.cc as "CC. Padrão",
            (nf.filial + 11000) as "Proj. Padrão",
            1 as "Seq. Item",
            {item} as "Cód Item",
            1 as "Quant. Item",
            p.valor as "Vlr Unit.Item",
            0 as "Descto",
            0 as "Acrescimo",
            p.valor as "Total Item",
            90 as "CST ICMS",
            85 as "APL.",
            nf.documento as "Nº DOC.",
            1 as "Parcela",
            date_format(p.vencimento, '%d/%m/%Y') as "Venc.",
            p.valor as "Valor Parcela",
            11 as "ORG.",
            cc.cc as "C.C.",    
            (nf.filial + 11000) as "Proj. Padrão"
        from nf_nf nf
        left join fornecedor_fornecedor f on f.id = nf.fornecedor_id
        left join nf_rateio r on r.nf_id = nf.id
        left join nf_parcela p on p.nf_id = nf.id
        left join core_contacontabil c on c.id = nf.conta_id
        left join core_centrodecusto cc on cc.id = r.cc_id
        where
            nf.tipo = 'F' 
            and nf.emissao between '{ini}' and '{fim}' 
            {where}
        order by nf.filial
        """
        #print(sql)
        return self.read_sql(sql)

def tab():
    return print(f"{'-'*50}\n")   

try:
    while True:
        tab()

        print('# # # # # RELATÓRIO IMPORTAÇÃO MEGA # # # # #\n')
        tab()
        
        print("""SELECIONE O TIPO DE RELATÓRIO:\n\n
        1. Contas de Serviço de Internet
        2. Contas da SUPERA
        3. Contas do IFOOD
        """)
        
        opcao = input('Digite a Opção desejada: ')

        select = False
        title = 'Relatório Conta Internet'
        where = 'and c.conta = 471'
        item = 29382
        serie = 'U'

        if opcao == '2':
            select = True
            title = 'Relatório SUPERA'
            where = 'and nf.fornecedor_id = 1683'
            item = 118999
            serie = 'E'

        elif opcao == '3':
            select = True
            title = 'Relatório IFOOD'
            where = 'and nf.fornecedor_id = 1684'
            item = 149321
            serie = '5'

        tab()

        
        ini = input('Digite a data INICAIL [Formato: dd/mm/aaaa]: ')
        fim = input('Digite a data FINAL [Formato: dd/mm/aaaa]: ')

        #ini = '01/05/2023'
        #fim = '08/05/2023'

        db = Database()
        print(f'Gerando {title} referente à {ini} à {fim}...')
        ini = ini.split('/')
        ini = f"{ini[-1]}-{ini[-2]}-{ini[-3]}"
        fim = fim.split('/')
        fim = f"{fim[-1]}-{fim[-2]}-{fim[-3]}"

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        

        df = db.relatorio_mega(ini, fim, where, item, serie)

        df['CC. Padrão'].fillna(0, inplace=True)
        df = df[df["CC. Padrão"] != 0]
        hoje = datetime.now().strftime('%Y%m%d%H%M%S')

        if select:        
            file = f"{desktop_path}/{title} - {ini} à {fim} ({hoje}).xlsx"
            df.to_excel(file, index=False)
            print(f'Salvando Arquivo em: {file}')

        else:        
            df['tipo'] = df['NF'].map(lambda x: str(x).split('-'))
            df.tipo = df.tipo.map(lambda x: '21' if len(x) == 1 else str(x[-1]).strip()).astype('str')

            df_21 = df[df.tipo != '22']
            df_22 = df[df.tipo == '22']

            del df_21['tipo']
            del df_22['tipo']        
            
            file_21 = f"{desktop_path}/{title} (21) - {ini} à {fim} ({hoje}).xlsx"
            file_22 = f"{desktop_path}/{title} (22) - {ini} à {fim} ({hoje}).xlsx"

            if len(df_21) > 0:
                print(f'Salvando Arquivo em: {file_21}')    
                df_21.to_excel(file_21, index=False)
            
            if len(df_22) > 0:
                df_22.to_excel(file_22, index=False)
                print(f'Salvando Arquivo em: {file_22}')

        tab()
        opcao_continuar = input('Digite 0 e pressione enter pra sair ou apenas enter para Gerar outro Relatório: ')

        if opcao_continuar == '0':
            break
    
    

except Exception as error:
    tab()
    for e in error.args:
        print(e)


#input('Pressione Enter para sair')



"""
RELATÓRIO DE VERSÃO

2023-05-13
    Criado Relatório conforme solicitação do Fiscal

2023-05-17
    Alterado para trazer apenas Notas do Tipos 'F' (Notas Fiscais)

"""
