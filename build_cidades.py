"""
Gera 800 cidades x 5 concursos = 4.000 paginas + indice de cidades.

URLs criadas:
  /{slug-cidade}/concurso-pedagogo.html
  /{slug-cidade}/concurso-professor.html
  /{slug-cidade}/pss-professor.html
  /{slug-cidade}/concurso-educacao-infantil.html
  /{slug-cidade}/concurso-auxiliar-educacao-infantil.html
  /cidades/index.html  (lista de todas as cidades)

Cada pagina:
  - Head SEO completo (canonical, OG, JSON-LD Article + BreadcrumbList)
  - Conteudo unico por cidade+cargo (templates variados)
  - CTA topo e rodape para AulaGen
  - Links internos (home + outros concursos da mesma cidade)
"""

from __future__ import annotations

import datetime
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IBGE_JSON = ROOT / "ibge_municipios.json"
SITE = "https://planodeaulapronto.github.io"
AULAGEN = "https://www.aulagen.com.br/"

STICKY_BANNER = """<!-- AULAGEN-STICKY-BANNER start -->
<div id="aulagen-sticky-banner" style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 50%,#ec4899 100%);color:#fff;padding:12px 18px;position:sticky;top:0;z-index:9999;box-shadow:0 2px 14px rgba(0,0,0,.2);font-family:system-ui,sans-serif">
  <div style="max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
    <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:260px">
      <div style="background:rgba(255,255,255,.2);width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0">IA</div>
      <div style="line-height:1.3">
        <div style="font-weight:800;font-size:.98rem">AulaGen - IA para Professores</div>
        <div style="font-size:.82rem;opacity:.92">50+ ferramentas IA: planos, provas, atividades adaptadas e simulados de concursos.</div>
      </div>
    </div>
    <a href="https://www.aulagen.com.br/" target="_blank" rel="noopener" style="background:#fff;color:#4F46E5;padding:9px 18px;border-radius:7px;font-weight:800;text-decoration:none;font-size:.86rem;white-space:nowrap;box-shadow:0 4px 10px rgba(0,0,0,.15);flex-shrink:0">Conhecer &rarr;</a>
  </div>
</div>
<!-- AULAGEN-STICKY-BANNER end -->
"""

# ===========================================================================
# Cidades prioritarias (alem das 27 capitais)
# ===========================================================================

CAPITAIS = {
    "São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza",
    "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Goiânia", "Belém",
    "Porto Alegre", "São Luís", "Maceió", "Natal", "Teresina", "João Pessoa",
    "Aracaju", "Cuiabá", "Campo Grande", "Florianópolis", "Vitória",
    "Macapá", "Porto Velho", "Rio Branco", "Boa Vista", "Palmas",
}

MAJOR_CITIES = {
    # SP
    "Guarulhos","Campinas","São Bernardo do Campo","São José dos Campos","Santo André",
    "Ribeirão Preto","Osasco","Sorocaba","Mauá","São José do Rio Preto","Santos",
    "Mogi das Cruzes","Diadema","Jundiaí","Carapicuíba","Piracicaba","Bauru",
    "São Vicente","Itaquaquecetuba","Franca","Guarujá","Taubaté","Praia Grande",
    "Limeira","Suzano","Taboão da Serra","Sumaré","Barueri","Embu das Artes",
    "São Caetano do Sul","Marília","Indaiatuba","Cotia","Americana","Araraquara",
    "Jacareí","Presidente Prudente","Hortolândia","Rio Claro","Ferraz de Vasconcelos",
    "Itapevi","Atibaia","Itu","Bragança Paulista","Pindamonhangaba","Araçatuba",
    "Itapecerica da Serra","São Carlos","Salto","Mogi Guaçu","Botucatu","Catanduva",
    "Jaú","Tatuí","Tupã","Lorena","Cubatão","Caraguatatuba","Ourinhos","Birigui",
    # RJ
    "São Gonçalo","Duque de Caxias","Nova Iguaçu","Niterói","Belford Roxo",
    "São João de Meriti","Campos dos Goytacazes","Petrópolis","Volta Redonda",
    "Magé","Itaboraí","Macaé","Nova Friburgo","Cabo Frio","Angra dos Reis",
    "Resende","Teresópolis","Mesquita","Nilópolis","Maricá","Queimados","Itaguaí",
    "Rio das Ostras","Barra Mansa","Araruama","Saquarema","Três Rios","Itaperuna",
    # MG
    "Uberlândia","Contagem","Juiz de Fora","Betim","Montes Claros","Ribeirão das Neves",
    "Uberaba","Sete Lagoas","Governador Valadares","Ipatinga","Divinópolis","Santa Luzia",
    "Ibirité","Poços de Caldas","Patos de Minas","Pouso Alegre","Teófilo Otoni",
    "Barbacena","Sabará","Varginha","Conselheiro Lafaiete","Itabira","Araguari",
    "Ubá","Passos","Coronel Fabriciano","Muriaé","Ituiutaba","Lavras","Manhuaçu",
    "Alfenas","Itajubá","Araxá",
    # BA
    "Feira de Santana","Vitória da Conquista","Camaçari","Itabuna","Juazeiro",
    "Lauro de Freitas","Ilhéus","Jequié","Teixeira de Freitas","Alagoinhas",
    "Barreiras","Porto Seguro","Simões Filho","Paulo Afonso","Eunápolis",
    "Santo Antônio de Jesus","Valença","Candeias","Itapetinga","Guanambi",
    "Senhor do Bonfim","Irecê","Conceição do Coité",
    # RS
    "Caxias do Sul","Pelotas","Canoas","Santa Maria","Gravataí","Viamão",
    "Novo Hamburgo","São Leopoldo","Rio Grande","Alvorada","Passo Fundo",
    "Sapucaia do Sul","Uruguaiana","Santa Cruz do Sul","Cachoeirinha","Bagé",
    "Bento Gonçalves","Erechim","Guaíba","Lajeado","Ijuí","Cruz Alta","Vacaria",
    "Carazinho","Sapiranga","Esteio",
    # PR
    "Londrina","Maringá","Ponta Grossa","Cascavel","São José dos Pinhais",
    "Foz do Iguaçu","Colombo","Guarapuava","Paranaguá","Araucária","Toledo",
    "Apucarana","Pinhais","Campo Largo","Almirante Tamandaré","Umuarama",
    "Piraquara","Cambé","Campo Mourão","Sarandi","Francisco Beltrão",
    "Paranavaí","Arapongas","Pato Branco",
    # PE
    "Jaboatão dos Guararapes","Olinda","Caruaru","Petrolina","Paulista",
    "Cabo de Santo Agostinho","Camaragibe","Garanhuns","Vitória de Santo Antão",
    "Igarassu","São Lourenço da Mata","Abreu e Lima","Santa Cruz do Capibaribe",
    "Ipojuca","Serra Talhada","Arcoverde","Goiana","Bezerros",
    # CE
    "Caucaia","Juazeiro do Norte","Maracanaú","Sobral","Crato","Itapipoca",
    "Maranguape","Iguatu","Quixadá","Pacatuba","Aquiraz","Crateús","Canindé",
    "Russas","Tianguá","Limoeiro do Norte","Camocim",
    # PA
    "Ananindeua","Santarém","Marabá","Castanhal","Parauapebas","Itaituba",
    "Cametá","Bragança","Marituba","Abaetetuba","Tucuruí","Altamira",
    "Barcarena","Tailândia","Paragominas","Capanema",
    # MA
    "Imperatriz","São José de Ribamar","Timon","Caxias","Codó","Paço do Lumiar",
    "Açailândia","Bacabal","Balsas","Santa Inês","Pinheiro","Chapadinha",
    # GO
    "Aparecida de Goiânia","Anápolis","Rio Verde","Luziânia","Águas Lindas de Goiás",
    "Valparaíso de Goiás","Trindade","Formosa","Novo Gama","Itumbiara",
    "Senador Canedo","Catalão","Jataí","Planaltina","Caldas Novas","Cidade Ocidental",
    # SC
    "Joinville","Blumenau","São José","Chapecó","Itajaí","Criciúma","Lages",
    "Jaraguá do Sul","Palhoça","Balneário Camboriú","Brusque","Tubarão",
    "São Bento do Sul","Caçador","Rio do Sul","Concórdia","Camboriú",
    # ES
    "Serra","Vila Velha","Cariacica","Cachoeiro de Itapemirim","Linhares",
    "São Mateus","Colatina","Guarapari","Aracruz","Viana","Nova Venécia",
    # PB
    "Campina Grande","Santa Rita","Patos","Bayeux","Sousa","Cajazeiras",
    "Cabedelo","Guarabira","Itabaiana","Mamanguape","Pombal",
    # RN
    "Mossoró","Parnamirim","São Gonçalo do Amarante","Macaíba","Ceará-Mirim",
    "Caicó","Açu","Currais Novos","Apodi","Pau dos Ferros",
    # AL
    "Arapiraca","Rio Largo","Palmeira dos Índios","União dos Palmares","Penedo",
    "São Miguel dos Campos","Coruripe","Delmiro Gouveia",
    # PI
    "Parnaíba","Picos","Floriano","Piripiri","Campo Maior","Barras","União",
    "Esperantina","São Raimundo Nonato",
    # SE
    "Nossa Senhora do Socorro","Lagarto","Itabaiana","São Cristóvão","Estância",
    "Tobias Barreto","Propriá","Itabaianinha",
    # MT
    "Várzea Grande","Rondonópolis","Sinop","Tangará da Serra","Cáceres","Sorriso",
    "Lucas do Rio Verde","Barra do Garças","Primavera do Leste","Nova Mutum",
    "Pontes e Lacerda","Alta Floresta",
    # MS
    "Dourados","Três Lagoas","Corumbá","Ponta Porã","Naviraí","Nova Andradina",
    "Aquidauana","Sidrolândia","Maracaju",
    # AM
    "Parintins","Itacoatiara","Manacapuru","Coari","Tabatinga","Tefé","Maués",
    "Iranduba","Humaitá","Lábrea",
    # AP
    "Santana","Laranjal do Jari","Oiapoque","Mazagão","Porto Grande",
    # RO
    "Ji-Paraná","Ariquemes","Vilhena","Cacoal","Rolim de Moura","Guajará-Mirim",
    "Jaru","Ouro Preto do Oeste",
    # RR
    "Rorainópolis","Caracaraí","Mucajaí","Alto Alegre",
    # AC
    "Cruzeiro do Sul","Sena Madureira","Tarauacá","Feijó","Brasiléia",
    # TO
    "Araguaína","Gurupi","Porto Nacional","Paraíso do Tocantins",
    "Colinas do Tocantins","Guaraí","Tocantinópolis",
}

# Quotas por estado (alvo total ~= 800)
QUOTA = {
    "SP": 130, "MG": 75, "BA": 50, "RS": 50, "PR": 50, "RJ": 45,
    "SC": 35, "GO": 32, "PE": 30, "CE": 28, "PA": 28, "MA": 25,
    "AM": 22, "PB": 22, "RN": 20, "ES": 20, "MT": 20, "PI": 18,
    "AL": 18, "TO": 15, "MS": 15, "SE": 12, "RO": 12, "AC": 8,
    "AP": 7, "RR": 6, "DF": 1
}
# total = 800 (com DF=1 = Brasilia)


# ===========================================================================
# Concursos
# ===========================================================================

CONCURSOS = [
    {
        "slug": "concurso-pedagogo",
        "cargo": "Pedagogo",
        "cargo_plural": "Pedagogos",
        "etapa_foco": "gestao escolar e coordenacao pedagogica",
        "salario": "R$ 3.500 a R$ 8.000",
        "escolaridade": "Superior em Pedagogia",
        "atribuicoes": "Coordenar projetos pedagogicos, supervisionar planejamento de aulas, apoiar professores na implementacao da BNCC, mediar relacao entre escola, familia e alunos, e elaborar relatorios pedagogicos.",
        "temas_prova": "BNCC, LDB (Lei 9.394/96), Plano Nacional de Educacao (PNE), DCNs (Diretrizes Curriculares Nacionais), avaliacao da aprendizagem, gestao democratica, ECA, psicologia da educacao, didatica e curriculo.",
    },
    {
        "slug": "concurso-professor",
        "cargo": "Professor",
        "cargo_plural": "Professores",
        "etapa_foco": "ensino regular em uma area especifica",
        "salario": "R$ 2.800 a R$ 7.500",
        "escolaridade": "Superior em Licenciatura na area",
        "atribuicoes": "Ministrar aulas alinhadas a BNCC, elaborar planos de aula, aplicar avaliacoes, registrar frequencia e notas, atender pais, participar de conselhos de classe e formacao continuada.",
        "temas_prova": "BNCC (com enfase na area de atuacao), LDB, conhecimentos especificos do componente curricular, didatica, metodologias ativas, avaliacao da aprendizagem, ECA, legislacao educacional, conhecimentos pedagogicos gerais.",
    },
    {
        "slug": "pss-professor",
        "cargo": "Professor PSS",
        "cargo_plural": "Professores PSS",
        "etapa_foco": "contratacao temporaria por Processo Seletivo Simplificado",
        "salario": "R$ 2.200 a R$ 5.500",
        "escolaridade": "Superior em Licenciatura ou Magisterio",
        "atribuicoes": "Atuar em substituicao a professores efetivos, lecionar conforme escala da rede municipal/estadual, cumprir a carga horaria e o calendario letivo, e elaborar planejamentos alinhados a BNCC.",
        "temas_prova": "Analise de titulos (graduacao, pos, experiencia), prova objetiva em conhecimentos pedagogicos e especificos da area, e avaliacao da BNCC do segmento. Em alguns editais ha entrevista ou prova didatica.",
    },
    {
        "slug": "concurso-educacao-infantil",
        "cargo": "Professor de Educacao Infantil",
        "cargo_plural": "Professores de Educacao Infantil",
        "etapa_foco": "berçario, maternal e pre-escola (0 a 5 anos)",
        "salario": "R$ 2.500 a R$ 5.800",
        "escolaridade": "Superior em Pedagogia ou Magisterio com habilitacao em Educacao Infantil",
        "atribuicoes": "Atender criancas de 0 a 5 anos respeitando os Campos de Experiencia da BNCC, planejar rotinas integradas (cuidado e educacao), promover desenvolvimento integral, registrar observacoes e elaborar relatorios de desenvolvimento.",
        "temas_prova": "BNCC Educacao Infantil (Campos de Experiencia e Direitos de Aprendizagem), DCNEI, LDB, ECA, desenvolvimento infantil (Piaget, Vygotsky, Wallon), praticas de cuidado e educacao, ludico e brincar, alfabetizacao emergente.",
    },
    {
        "slug": "concurso-auxiliar-educacao-infantil",
        "cargo": "Auxiliar de Educacao Infantil",
        "cargo_plural": "Auxiliares de Educacao Infantil",
        "etapa_foco": "apoio a professor titular em creche e pre-escola",
        "salario": "R$ 1.700 a R$ 3.400",
        "escolaridade": "Ensino Medio completo, preferencialmente Magisterio",
        "atribuicoes": "Auxiliar o professor titular nas atividades de cuidado e educacao das criancas, apoiar na alimentacao, higiene, sono e atividades pedagogicas, zelar pela seguranca e bem-estar das criancas.",
        "temas_prova": "Lingua Portuguesa, Matematica basica, conhecimentos gerais sobre Educacao Infantil, BNCC (Campos de Experiencia), ECA, primeiros socorros, higiene e nutricao infantil, atividades ludicas e pedagogicas adequadas a faixa etaria.",
    },
]


# ===========================================================================
# Helpers
# ===========================================================================

def slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", text)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def select_800_cities() -> list[dict]:
    raw = json.loads(IBGE_JSON.read_text(encoding="utf-8"))
    # index por UF -> [cidades]
    by_uf: dict[str, list[dict]] = {}
    for c in raw:
        nome = c["nome"]
        try:
            uf = c["microrregiao"]["mesorregiao"]["UF"]["sigla"]
            uf_nome = c["microrregiao"]["mesorregiao"]["UF"]["nome"]
            regiao = c["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
        except (KeyError, TypeError):
            continue
        by_uf.setdefault(uf, []).append({
            "nome": nome, "uf": uf, "uf_nome": uf_nome,
            "regiao": regiao, "slug": slugify(nome),
        })

    selecionadas: list[dict] = []
    for uf, lista in by_uf.items():
        cota = QUOTA.get(uf, 5)
        # ordena: capital primeiro, depois major, depois alfabetico
        def score(c: dict) -> tuple:
            n = c["nome"]
            return (
                0 if n in CAPITAIS else (1 if n in MAJOR_CITIES else 2),
                n,
            )
        lista.sort(key=score)
        selecionadas.extend(lista[:cota])

    # remove duplicatas por slug (pode haver slug igual em estados diferentes)
    seen: set[str] = set()
    final = []
    for c in selecionadas:
        key = f"{c['slug']}-{c['uf']}"
        if key in seen:
            continue
        seen.add(key)
        # se slug colidir entre estados, sufixa com -UF
        slug = c["slug"]
        if any(x["slug"] == slug for x in final):
            c["slug"] = f"{slug}-{c['uf'].lower()}"
        final.append(c)
    return final


# ===========================================================================
# Templates HTML
# ===========================================================================

def render_page(cidade: dict, concurso: dict, outros_concursos: list[dict]) -> str:
    cargo = concurso["cargo"]
    cidade_nome = cidade["nome"]
    uf = cidade["uf"]
    uf_nome = cidade["uf_nome"]
    regiao = cidade["regiao"]
    slug_cidade = cidade["slug"]
    slug_concurso = concurso["slug"]

    title = f"{cargo} em {cidade_nome}/{uf} — Guia do Concurso e Material de Estudo"
    desc = (
        f"Guia completo do {cargo} para concurso publico em {cidade_nome}/{uf}: "
        f"atribuicoes, salario, escolaridade, temas da prova ({concurso['temas_prova'][:80]}...) "
        f"e material de estudo com IA AulaGen."
    )[:160]
    canonical = f"{SITE}/{slug_cidade}/{slug_concurso}.html"

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Cidades", "item": f"{SITE}/cidades/"},
            {"@type": "ListItem", "position": 3, "name": f"{cidade_nome}/{uf}", "item": f"{SITE}/{slug_cidade}/"},
            {"@type": "ListItem", "position": 4, "name": cargo, "item": canonical},
        ],
    }
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "url": canonical,
        "datePublished": "2026-01-01",
        "dateModified": datetime.date.today().isoformat(),
        "inLanguage": "pt-BR",
        "author": {"@type": "Organization", "name": "Plano de Aula Pronto"},
        "publisher": {"@type": "Organization", "name": "Plano de Aula Pronto", "url": f"{SITE}/"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }

    # gentilico aproximado baseado em padrao comum (nao perfeito, mas evita texto identico)
    seed = sum(ord(c) for c in cidade_nome) % 4
    intros = [
        f"O municipio de <strong>{cidade_nome}</strong>, localizado no estado {uf_nome} ({uf}), regiao {regiao}, oferece oportunidades reais para quem busca uma carreira estavel como {cargo}. A rede municipal e estadual em {cidade_nome} segue as diretrizes da BNCC e da LDB, e os concursos sao a porta de entrada para o servico publico na area da educacao.",
        f"Quer se tornar {cargo} em <strong>{cidade_nome} ({uf})</strong>? Esta pagina reune as principais informacoes que voce precisa saber sobre o concurso publico de {cidade_nome}, no {uf_nome}, regiao {regiao}: requisitos, conteudo da prova, salario e como se preparar com IA da AulaGen.",
        f"<strong>{cidade_nome}</strong>, no {uf_nome} ({uf}), e uma das cidades brasileiras da regiao {regiao} com demanda recorrente por {concurso['cargo_plural']}. As prefeituras e Secretarias de Educacao realizam concursos publicos periodicos para preencher vagas em escolas municipais e estaduais, com salarios atrativos e estabilidade.",
        f"Pensa em prestar concurso para {cargo} em <strong>{cidade_nome}/{uf}</strong>? Voce esta no lugar certo. {cidade_nome}, situada na regiao {regiao} do Brasil, no estado {uf_nome}, oferece carreira solida no setor publico da educacao com plano de cargos, beneficios e progressao.",
    ]

    # CTAs
    cta_top = f'''<div style="background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%);color:#fff;padding:22px 26px;border-radius:14px;margin:24px 0;box-shadow:0 6px 18px rgba(79,70,229,.25)">
  <div style="font-size:.74rem;font-weight:800;letter-spacing:.5px;opacity:.9;margin-bottom:6px">⚡ PREPARACAO COM IA</div>
  <h2 style="color:#fff;margin:0 0 10px;font-size:1.25rem">Estude para o concurso de {html.escape(cargo)} em {html.escape(cidade_nome)} com IA</h2>
  <p style="margin:0 0 14px;font-size:.96rem;color:#eef0fb">Crie simulados, listas de questoes por edital, resumos de LDB/BNCC/ECA e roteiros de estudo personalizados. O AulaGen tem 50+ ferramentas de IA para professores e candidatos a concursos da educacao.</p>
  <a href="{AULAGEN}" target="_blank" rel="noopener" style="display:inline-block;background:#fff;color:#4F46E5;padding:11px 22px;border-radius:8px;font-weight:800;text-decoration:none;font-size:.92rem">Conhecer o AulaGen &rarr;</a>
</div>'''

    cta_bottom = f'''<div style="background:#f8fafc;border:2px solid #4F46E5;padding:28px;border-radius:16px;margin:36px 0 10px;text-align:center">
  <h2 style="color:#4F46E5;margin:0 0 12px;font-size:1.4rem">Pronto para passar no concurso de {html.escape(cidade_nome)}?</h2>
  <p style="color:#2d3748;margin:0 0 18px;font-size:1rem;max-width:560px;margin-left:auto;margin-right:auto;line-height:1.55">
    A <strong>AulaGen</strong> entrega questoes comentadas, simulados por cargo, plano de estudos por edital e material da BNCC e legislacao educacional — tudo gerado com IA, alinhado ao perfil do concurso de {html.escape(cargo)}.
  </p>
  <ul style="list-style:none;padding:0;margin:0 0 22px;display:inline-block;text-align:left">
    <li style="margin:5px 0;color:#2d3748">&check; Questoes de LDB, ECA, BNCC e DCNs com gabarito comentado</li>
    <li style="margin:5px 0;color:#2d3748">&check; Simulados especificos para {html.escape(cargo)}</li>
    <li style="margin:5px 0;color:#2d3748">&check; Plano de estudos por cidade e edital</li>
    <li style="margin:5px 0;color:#2d3748">&check; Resumos visuais e mapas mentais</li>
    <li style="margin:5px 0;color:#2d3748">&check; A partir de <strong>R$ 39,90/mes</strong></li>
  </ul>
  <div>
    <a href="{AULAGEN}" target="_blank" rel="noopener" style="display:inline-block;background:#4F46E5;color:#fff;padding:14px 32px;border-radius:10px;font-weight:800;text-decoration:none;font-size:1.05rem;box-shadow:0 6px 14px rgba(79,70,229,.3)">Comecar a estudar com IA &rarr;</a>
  </div>
</div>'''

    # links para outros concursos da mesma cidade
    outros_links = "\n".join(
        f'<li style="margin:8px 0"><a href="{c["slug"]}.html" style="color:#4F46E5;text-decoration:none">&rarr; {c["cargo"]} em {html.escape(cidade_nome)}/{uf}</a></li>'
        for c in outros_concursos
    )

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="Plano de Aula Pronto">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Plano de Aula Pronto">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(article_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
<style>
:root {{ --primary:#4F46E5; --dark:#1a1a2e; --text:#2d3748; }}
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Inter','Open Sans',sans-serif; color:var(--text); background:#f8fafc; line-height:1.6; }}
.nav-bar {{ background:#fff; padding:14px 20px; box-shadow:0 2px 10px rgba(0,0,0,.08); position:sticky; top:0; z-index:100; display:flex; justify-content:space-between; align-items:center; }}
.logo {{ font-weight:800; color:var(--primary); text-decoration:none; font-size:1.15rem; }}
.nav-bar nav a {{ color:var(--text); font-weight:600; text-decoration:none; margin-left:18px; font-size:.92rem; }}
.crumb {{ background:#eef2ff; padding:12px 20px; font-size:.85rem; color:#4F46E5; }}
.crumb a {{ color:#4F46E5; text-decoration:none; }}
.container {{ max-width:880px; margin:30px auto; padding:0 20px; }}
.content-area {{ background:#fff; padding:40px; border-radius:16px; box-shadow:0 4px 20px rgba(0,0,0,.05); }}
h1 {{ font-size:1.9rem; color:var(--dark); margin-bottom:16px; line-height:1.25; }}
h2 {{ font-size:1.35rem; color:var(--dark); margin:28px 0 12px; }}
h3 {{ font-size:1.1rem; color:var(--dark); margin:20px 0 8px; }}
p, li {{ margin-bottom:12px; }}
ul {{ margin:8px 0 16px 22px; }}
.info-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:16px; margin:24px 0; padding:20px; background:#eef2ff; border-radius:12px; }}
.info-grid div b {{ display:block; font-size:.78rem; color:#4F46E5; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }}
.related-list {{ background:#f8fafc; padding:20px; border-radius:12px; margin-top:30px; list-style:none; margin-left:0; }}
.related-list li {{ margin:0; }}
.footer {{ background:#1a1a2e; color:#a0aec0; padding:30px 20px; text-align:center; font-size:.85rem; margin-top:40px; }}
.footer a {{ color:#a0aec0; text-decoration:none; }}
@media (max-width:600px){{ .content-area{{padding:24px}} h1{{font-size:1.55rem}} .info-grid{{grid-template-columns:1fr}} }}
</style>
</head>
<body>

{STICKY_BANNER}

<nav class="nav-bar">
  <a href="../index.html" class="logo">📚 Plano de Aula Pronto</a>
  <nav>
    <a href="../index.html">Inicio</a>
    <a href="../artigos/">Blog</a>
    <a href="../cidades/">Cidades</a>
    <a href="{AULAGEN}" target="_blank" rel="noopener" style="color:#4F46E5;font-weight:800">AulaGen ↗</a>
  </nav>
</nav>

<div class="crumb">
  <a href="../">Inicio</a> &rsaquo;
  <a href="../cidades/">Cidades</a> &rsaquo;
  <a href="./">{html.escape(cidade_nome)}/{uf}</a> &rsaquo;
  <span>{html.escape(cargo)}</span>
</div>

<div class="container">
<article class="content-area">

<h1>{html.escape(cargo)} em {html.escape(cidade_nome)}/{uf} — Guia do Concurso</h1>

<p>{intros[seed]}</p>

{cta_top}

<div class="info-grid">
  <div><b>Cidade</b>{html.escape(cidade_nome)}</div>
  <div><b>Estado</b>{html.escape(uf_nome)} ({uf})</div>
  <div><b>Regiao</b>{html.escape(regiao)}</div>
  <div><b>Cargo</b>{html.escape(cargo)}</div>
  <div><b>Escolaridade</b>{html.escape(concurso["escolaridade"])}</div>
  <div><b>Salario estimado</b>{html.escape(concurso["salario"])}</div>
</div>

<h2>Quem pode prestar o concurso de {html.escape(cargo)} em {html.escape(cidade_nome)}?</h2>
<p>Para o cargo de <strong>{html.escape(cargo)}</strong> nas redes publicas de {html.escape(cidade_nome)}, geralmente exige-se <strong>{html.escape(concurso["escolaridade"])}</strong>. Alguns editais municipais e estaduais do {html.escape(uf_nome)} tambem aceitam habilitacoes equivalentes ou pos-graduacao na area educacional.</p>

<h2>Atribuicoes do cargo</h2>
<p>O {html.escape(cargo)} aprovado em concurso de {html.escape(cidade_nome)} atua principalmente em {html.escape(concurso["etapa_foco"])}. Entre as atribuicoes esperadas estao:</p>
<p>{html.escape(concurso["atribuicoes"])}</p>

<h2>Temas mais cobrados nas provas</h2>
<p>Os concursos para {html.escape(cargo)} em municipios como {html.escape(cidade_nome)} costumam cobrar:</p>
<p>{html.escape(concurso["temas_prova"])}</p>

<h3>Conhecimentos pedagogicos gerais (cai em todos os editais)</h3>
<ul>
  <li>LDB — Lei de Diretrizes e Bases da Educacao Nacional (Lei 9.394/96)</li>
  <li>ECA — Estatuto da Crianca e do Adolescente (Lei 8.069/90)</li>
  <li>BNCC — Base Nacional Comum Curricular (alinhada a etapa do cargo)</li>
  <li>Plano Nacional de Educacao (PNE) e DCNs</li>
  <li>Avaliacao da aprendizagem, didatica, curriculo</li>
  <li>Inclusao escolar e Educacao Especial (Decreto 7.611/2011)</li>
</ul>

<h2>Como se preparar para o concurso de {html.escape(cargo)} em {html.escape(cidade_nome)}</h2>
<p>A preparacao eficaz combina <strong>leitura da legislacao</strong>, <strong>resolucao de questoes anteriores</strong> e <strong>simulados frequentes</strong>. A AulaGen automatiza essa rotina: voce informa o cargo, a cidade e a banca, e a IA gera plano de estudos, simulados comentados e resumos.</p>

<ol style="margin:12px 0 18px 22px">
  <li>Leia o edital atual da prefeitura de {html.escape(cidade_nome)} (ou Secretaria de Educacao do {html.escape(uf_nome)}) quando publicado.</li>
  <li>Faca um diagnostico: resolva 20 questoes de cada tema do edital para identificar pontos fracos.</li>
  <li>Monte uma rotina de estudos de 4 a 8 semanas com simulados semanais.</li>
  <li>Use IA (AulaGen) para gerar questoes especificas de LDB/ECA/BNCC com gabarito comentado.</li>
  <li>Revise por mapas mentais e resumos.</li>
</ol>

{cta_bottom}

<h2>Outros concursos da educacao em {html.escape(cidade_nome)}</h2>
<ul class="related-list">
{outros_links}
</ul>

<h2>Sobre {html.escape(cidade_nome)}, {uf_nome}</h2>
<p>{html.escape(cidade_nome)} e um municipio brasileiro situado no estado {html.escape(uf_nome)}, na regiao {html.escape(regiao)} do pais. A educacao publica em {html.escape(cidade_nome)} e coordenada pela Secretaria Municipal de Educacao em conjunto com a Secretaria Estadual de Educacao do {html.escape(uf_nome)}, oferecendo Educacao Infantil, Ensino Fundamental I e II e, em algumas escolas estaduais, Ensino Medio.</p>

<p style="font-size:.9rem;color:#666;margin-top:30px;border-top:1px solid #eee;padding-top:18px">Pagina informativa sobre concurso de {html.escape(cargo)} em {html.escape(cidade_nome)}/{uf}. As informacoes de salario e atribuicoes sao estimativas baseadas em editais tipicos — sempre consulte o edital oficial publicado pela prefeitura ou pela Secretaria de Educacao competente.</p>

</article>
</div>

<footer class="footer">
  <p>© 2026 Plano de Aula Pronto · Estude com IA na <a href="{AULAGEN}" target="_blank" rel="noopener" style="color:#fff;text-decoration:underline">AulaGen</a> · planodeaulaprontobncc@gmail.com</p>
</footer>

</body>
</html>'''


# ===========================================================================
# Indice de cidades (/cidades/index.html)
# ===========================================================================

def render_cidades_index(cidades: list[dict]) -> str:
    # agrupa por UF
    by_uf: dict[str, list[dict]] = {}
    for c in cidades:
        by_uf.setdefault(c["uf"], []).append(c)
    for uf in by_uf:
        by_uf[uf].sort(key=lambda c: c["nome"])

    secoes = []
    for uf in sorted(by_uf.keys()):
        uf_nome = by_uf[uf][0]["uf_nome"]
        links = "".join(
            f'<li style="margin:4px 0"><a href="../{c["slug"]}/concurso-pedagogo.html" style="color:#4F46E5;text-decoration:none">{html.escape(c["nome"])}</a></li>'
            for c in by_uf[uf]
        )
        secoes.append(f'''<section style="margin-bottom:30px">
  <h2 style="font-size:1.2rem;color:#1a1a2e;border-bottom:2px solid #4F46E5;padding-bottom:6px;margin-bottom:12px">{html.escape(uf_nome)} ({uf}) — {len(by_uf[uf])} cidades</h2>
  <ul style="list-style:none;padding:0;columns:3;column-gap:24px">{links}</ul>
</section>''')

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Concursos para Professor por Cidade — {len(cidades)} cidades do Brasil</title>
<meta name="description" content="Guia de concursos publicos para professor, pedagogo, educacao infantil e auxiliar em {len(cidades)} cidades brasileiras. Material de estudo com IA AulaGen.">
<link rel="canonical" href="{SITE}/cidades/">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website">
<meta property="og:title" content="Concursos para Professor por Cidade">
<style>
body {{ font-family:'Inter',sans-serif; color:#2d3748; background:#f8fafc; margin:0; line-height:1.6; }}
.nav-bar {{ background:#fff; padding:14px 20px; box-shadow:0 2px 10px rgba(0,0,0,.08); display:flex; justify-content:space-between; align-items:center; }}
.logo {{ font-weight:800; color:#4F46E5; text-decoration:none; font-size:1.15rem; }}
.container {{ max-width:1100px; margin:30px auto; padding:0 20px; }}
h1 {{ color:#1a1a2e; font-size:2rem; margin-bottom:10px; }}
.hero p {{ color:#4a5568; font-size:1.05rem; }}
.hero {{ background:linear-gradient(135deg,#4F46E5 0%,#7c3aed 100%); color:#fff; padding:50px 20px; text-align:center; }}
.hero h1 {{ color:#fff; }}
.hero p {{ color:#eef0fb; }}
.hero a {{ display:inline-block; background:#fff; color:#4F46E5; padding:12px 28px; border-radius:8px; font-weight:800; text-decoration:none; margin-top:14px; }}
@media (max-width:800px){{ ul[style*="columns:3"]{{column-count:2}} }}
@media (max-width:500px){{ ul[style*="columns:3"]{{column-count:1}} }}
</style>
</head>
<body>

{STICKY_BANNER}

<nav class="nav-bar">
  <a href="../index.html" class="logo">📚 Plano de Aula Pronto</a>
  <div><a href="../index.html" style="color:#2d3748;text-decoration:none;margin-right:14px">Inicio</a><a href="{AULAGEN}" target="_blank" rel="noopener" style="color:#4F46E5;font-weight:800;text-decoration:none">AulaGen ↗</a></div>
</nav>

<section class="hero">
  <h1>Concursos da Educacao por Cidade</h1>
  <p>{len(cidades)} municipios brasileiros · 5 cargos cada · {len(cidades)*5} guias completos</p>
  <a href="{AULAGEN}" target="_blank" rel="noopener">Estudar com IA no AulaGen &rarr;</a>
</section>

<div class="container">
  <p style="margin-bottom:24px">Escolha sua cidade e veja os concursos para <strong>Pedagogo, Professor, Professor PSS, Professor de Educacao Infantil e Auxiliar de Educacao Infantil</strong> — com atribuicoes, salario, conteudo da prova e material de estudo com IA.</p>
  {chr(10).join(secoes)}
</div>

<footer style="background:#1a1a2e;color:#a0aec0;padding:30px;text-align:center;margin-top:40px">© 2026 Plano de Aula Pronto · <a href="{AULAGEN}" target="_blank" rel="noopener" style="color:#fff;text-decoration:underline">AulaGen</a> · planodeaulaprontobncc@gmail.com</footer>

</body>
</html>'''


# ===========================================================================
# Atualiza sitemap
# ===========================================================================

def update_sitemap(cidades: list[dict]) -> int:
    today = datetime.date.today().isoformat()
    urls: dict[str, tuple[str, str]] = {}

    def add(loc: str, priority: str, freq: str = "monthly") -> None:
        urls[loc] = (priority, freq)

    add(f"{SITE}/", "1.0", "weekly")

    for name in ("mapa-do-site.html", "privacidade.html", "termos.html"):
        if (ROOT / name).exists():
            add(f"{SITE}/{name}", "0.5")

    for folder, priority in (
        ("discipline-pages", "0.9"),
        ("produtos", "0.8"),
        ("produto", "0.8"),
        ("artigos", "0.7"),
    ):
        base = ROOT / folder
        if base.is_dir():
            for html_file in sorted(base.glob("*.html")):
                add(f"{SITE}/{folder}/{html_file.name}", priority)

    if (ROOT / "cidades" / "index.html").exists():
        add(f"{SITE}/cidades/", "0.85", "weekly")

    for c in cidades:
        for k in CONCURSOS:
            page = ROOT / c["slug"] / f"{k['slug']}.html"
            if page.exists():
                add(f'{SITE}/{c["slug"]}/{k["slug"]}.html', "0.65")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc in sorted(urls):
        priority, freq = urls[loc]
        lines.append(f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{priority}</priority></url>')
    lines.append("</urlset>")

    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return len(urls)


# ===========================================================================
# Main
# ===========================================================================

def main() -> None:
    if not IBGE_JSON.exists():
        sys.exit("erro: ibge_municipios.json nao encontrado")

    print("Selecionando cidades...")
    cidades = select_800_cities()
    print(f"  -> {len(cidades)} cidades selecionadas")
    by_uf_count = {}
    for c in cidades:
        by_uf_count[c["uf"]] = by_uf_count.get(c["uf"], 0) + 1
    print("  distribuicao por UF:", dict(sorted(by_uf_count.items())))

    print(f"\nGerando {len(cidades) * len(CONCURSOS)} paginas...")
    total = 0
    for i, cidade in enumerate(cidades, 1):
        cidade_dir = ROOT / cidade["slug"]
        cidade_dir.mkdir(exist_ok=True)
        for j, concurso in enumerate(CONCURSOS):
            outros = [c for c in CONCURSOS if c["slug"] != concurso["slug"]]
            html_str = render_page(cidade, concurso, outros)
            (cidade_dir / f"{concurso['slug']}.html").write_text(html_str, encoding="utf-8", newline="\n")
            total += 1
        if i % 100 == 0:
            print(f"  ...{i}/{len(cidades)} cidades ({total} paginas)")

    print(f"\nTotal de paginas geradas: {total}")

    # indice de cidades
    print("\nGerando /cidades/index.html ...")
    cidades_dir = ROOT / "cidades"
    cidades_dir.mkdir(exist_ok=True)
    (cidades_dir / "index.html").write_text(render_cidades_index(cidades), encoding="utf-8", newline="\n")
    print("  -> ok")

    # sitemap
    print("\nAtualizando sitemap.xml ...")
    added = update_sitemap(cidades)
    print(f"  -> {added} URLs adicionadas")

    print("\nBuild concluido.")


if __name__ == "__main__":
    main()
