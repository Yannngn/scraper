# Web Scraper

{
  >"author": "Autor/Autora do conteúdo",

  >"body": "Corpo do conteúdo (transcrição da palestra ou todo o corpo de um artigo)",

  >"title": "Título da palestra ou artigo",

  >"type": "Tipo do conteúdo (deve ser exatamente article ou video)",

  >"url": "URL onde o conteúdo foi acessado"
  
}
"""

import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import json
import html

urls = ["https://www.ted.com/talks/helen_czerski_the_fascinating_physics_of_everyday_life/transcript?language=pt-br#t-81674",
        "https://www.ted.com/talks/kevin_kelly_how_ai_can_bring_on_a_second_industrial_revolution/transcript?language=pt-br",
        "https://www.ted.com/talks/sarah_parcak_help_discover_ancient_ruins_before_it_s_too_late/transcript?language=pt-br",
        "https://www.ted.com/talks/sylvain_duranton_how_humans_and_ai_can_work_together_to_create_better_businesses/transcript?language=pt-br",
        "https://www.ted.com/talks/chieko_asakawa_how_new_technology_helps_blind_people_explore_the_world/transcript?language=pt-br",
        "https://www.ted.com/talks/pierre_barreau_how_ai_could_compose_a_personalized_soundtrack_to_your_life/transcript?language=pt-br",
        "https://www.ted.com/talks/tom_gruber_how_ai_can_enhance_our_memory_work_and_social_lives/transcript?language=pt-br",
        "https://olhardigital.com.br/colunistas/wagner_sanchez/post/o_futuro_cada_vez_mais_perto/78972",
        "https://olhardigital.com.br/colunistas/wagner_sanchez/post/os_riscos_do_machine_learning/80584",
        "https://olhardigital.com.br/ciencia-e-espaco/noticia/nova-teoria-diz-que-passado-presente-e-futuro-coexistem/97786",
        "https://olhardigital.com.br/noticia/inteligencia-artificial-da-ibm-consegue-prever-cancer-de-mama/87030",
        "https://olhardigital.com.br/ciencia-e-espaco/noticia/inteligencia-artificial-ajuda-a-nasa-a-projetar-novos-trajes-espaciais/102772",
        "https://olhardigital.com.br/colunistas/jorge_vargas_neto/post/como_a_inteligencia_artificial_pode_mudar_o_cenario_de_oferta_de_credito/78999",
        "https://olhardigital.com.br/ciencia-e-espaco/noticia/cientistas-criam-programa-poderoso-que-aprimora-deteccao-de-galaxias/100683",
        "https://www.startse.com/noticia/startups/mobtech/deep-learning-o-cerebro-dos-carros-autonomos"
       ]

def to_text(obj) :
  text = obj[0].get_text()
  for i in range(1, len(obj)) :  
    text = text + obj[i].get_text()

  return text

def to_dict(data):
  dic = []
  for i in range(data.shape[0]):
    dic.append(dict(data.loc[i,:]))
  return dic

df = pd.DataFrame(columns=["author", "body", "title", "type", "url"])
df.url = urls

for url in urls :
  req = requests.get(url)
  req.encoding = "UTF8"
  
  if req.status_code == 200:
      print('Requisição bem sucedida!')

  content = BeautifulSoup(req.content, 'html.parser')
  df.at[df[df.url == url].index[0], "title"] = content.title.string
  df.at[df[df.url == url].index[0], "author"] = content.find("meta",  {"name":"author"})['content']
  if str("www.ted.com/talks") in url :
    obj = content.findAll("div",  {"class":"Grid__cell flx-s:1 p-r:4"}) 
    df.at[df[df.url == url].index[0], "body"] = to_text(obj)
    df.at[df[df.url == url].index[0], "type"] = "video"
  elif str("olhardigital.com.br") in url :
    df.at[df[df.url == url].index[0], "type"] = content.find("meta",  property="og:type")['content']
    content = BeautifulSoup(req.content, 'html.parser')
    body = content.findAll('script',attrs={'type':"application/ld+json"})[0].text.strip("articleBody").partition('"articleBody" : ')[2].partition('"url" : ')[0][1:-1]
    df.at[df[df.url == url].index[0], "body"] = html.unescape(body)
  else :
    df.at[df[df.url == url].index[0], "type"] = content.find("meta",  property="og:type")['content']
    html = content.findAll("span", {"style":"font-weight: 400;"})
    df.at[df[df.url == url].index[0], "body"] = to_text(html)

for i in range(df.body.size) :
  df.body[i] = re.sub('\s+', ' ', df.body[i])

to_dict(df)

from_json = to_dict(df)
for i in range(len(from_json)):
  with open('url_{}.json'.format(i), 'w', encoding='utf-8') as f:
      json.dump(from_json[i], f, ensure_ascii=False, indent=4)
  print('Criação de json bem sucedida!')
