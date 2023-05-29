import requests
import pandas as pd
import numpy as np
import yagmail
import os
import mysql.connector
from datetime import date

import warnings
warnings.filterwarnings('ignore')

from local_settings import host, port, user, password, database, email_user, email_password, email_host, email_port, to_fiscal, cc_fiscal, HOST_SITE

hoje = date.today()
qtde_nf_lote = 20

print('Conectando ao e-mail CONTROLADORIA@DROGAL.COM.BR')


def enviar_email(titulo, anexo):
    usuario = yagmail.SMTP(email_user, email_password, host=email_host, port=email_port,
                           smtp_starttls=True, smtp_ssl=False)
    to = to_fiscal
    cc = cc_fiscal
    mensagem = """*** Importação Automática - NÃO RESPONDA ESSE E-MAIL ***"""
    usuario.send(to=to, cc=cc, subject=titulo, contents=mensagem, attachments=anexo)


print('Conectando à HOSTMÍDIA ...')

conn = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

print('Recuperando NF´s não importadas')
sql = """
select nf.id, nf.data_inclusao, f.nome, nf.filial, nf.documento, nf.arquivo , rn.data
from nf_nf nf 
left join fornecedor_fornecedor f on f.id = nf.fornecedor_id 
left join nf_registrosnota rn on rn.nf_id = nf.id
where nf.importado = 0 and nf.status=5 and rn.registro like '%NF Finalizada%'
"""

df = pd.read_sql(sql, conn)
conn.close()

qtde_notas = len(df)
i = 1
arquivos = []
nfs = []

if qtde_notas > 0:
    lotes = int(np.ceil(qtde_notas / qtde_nf_lote))
    print(f'{qtde_notas} arquivos Recuperados...')
    print('Preparando Arquivos para Download...')
    for d in df.itertuples():
        nfs.append(str(d.id))
        try:
            URL = f"{HOST_SITE}/{d.arquivo}"
            file = requests.get(URL, stream=True)

            path_raiz = r"G:\Fiscal\Notas Fiscais"
            fl = d.filial if d.filial not in (98, 99) else 99
            filial = 'FL {:03d}'.format(fl) if fl in (1, 36, 65, 99, 196) else 'Filiais'
            if d.data.day <= 10:
                december = '1º DEC'
            elif d.data.day <= 20:
                december = '2º DEC'
            else:
                december = '3º DEC'
            path_name = r"{}\{}\Notas Fiscais {}-{}\{}\{}".format(path_raiz, d.data.year,
                                                                  '{:02d}'.format(d.data.month),
                                                                  d.data.year, filial, december)
            try:
                os.makedirs(path_name)
                print(f'Criando Diretório: {path_name}')
            except:
                pass

            # print(f'Importando Arquivos: {i}/{qtde_notas}')
            file_name = r"""{}\Filial {} - NF {} - {}.pdf""".format(path_name, '{:03d}'.format(d.filial),
                                                                    d.documento.replace('/', '-'),
                                                                    d.nome.replace('/', '-'))

            print(file_name)
            with open(file_name, "wb") as pdf:
                for chunk in file.iter_content(chunk_size=1024):
                    if chunk:
                        pdf.write(chunk)

                        arquivos.append(file_name)
                        i += 1
        except:
            print('### Erro ao importar o arquivo ###')
            print(file_name)

    print('Preparando para envio de E-mail...')
    email = 1
    try:
        for l in range(lotes):
            if len(arquivos) > qtde_nf_lote:
                anexos = arquivos[:qtde_nf_lote]
                del (arquivos[:qtde_nf_lote])
            else:
                anexos = arquivos
                arquivos = []
            titulo = f"Importação {'{:02d}'.format(hoje.day)}/{'{:02d}'.format(hoje.month)}/{hoje.year} - Lote: {l + 1}/{lotes}"

            enviar_email(titulo, anexos)
            print(titulo)
    except:
        print("Erro ao enviar o E-mail")

    print('Atualizando Banco de Dados')
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    conn.cursor().execute(f"update nf_nf set importado = 1 where id in ({', '.join(nfs)})")
    conn.commit()
    conn.close()

    print(nfs)

    print('Importação Finalizada')
else:
    print('Não há NFS para importar')


input('Pessione Enter para Sair')
