# Laboratório de incidência tributária

**Luis Felipe Tarouquela Contreras · Economia aplicada, tributação e desigualdade**

Ferramenta em Python para analisar a incidência distributiva de um tributo e de sua devolução. Relacionada à agenda de pesquisa de mestrado no PPGE/UFF sobre cashback, cesta básica e regressividade com a POF 2017–2018.

**Estado da evidência:** este projeto oferece código verificável e um painel para carregar resultados. Não contém resultados empíricos da dissertação nem constitui sua replicação. As tabelas, o tratamento dos microdados e as regras dos cenários precisam ser incorporados para essa finalidade. Dados artificiais aparecem nos testes e no modo demonstrativo do painel, sempre identificados como fictícios.

## Executar

Requer Python 3.10 ou superior, sem bibliotecas externas.

```sh
python -m unittest -v
python incidence.py sua_base.csv --output resultados.json --source "POF 2017–2018; versão e processamento" --scenario "Descrição completa do cenário" --unit "Unidade, periodicidade e conceito dos pesos"
```

Abra `index.html` em um navegador e carregue `resultados.json`. O processamento do painel ocorre localmente; o arquivo não é enviado a um servidor. Não publique microdados identificáveis. O código Python exporta somente agregados.

## Contrato de entrada

CSV UTF-8 com cabeçalho `income,tax_before,cashback,weight`. Uma linha representa uma unidade analítica; valores monetários devem estar na mesma periodicidade e base de preços. `income` é renda pré-tributação; `tax_before` é o tributo do cenário antes do cashback, **não necessariamente a tributação anterior à reforma**; `cashback` é a devolução do mesmo cenário; `weight` é o peso de expansão.

Defina explicitamente a população: para análise por pessoas, use valores per capita e pesos de pessoas; para domicílios, use valores e pesos domiciliares. O módulo ordena pela coluna `income`. Não misture renda domiciliar total com ordenação per capita sem adaptar e documentar o procedimento.

Exigem-se renda e peso positivos e 0 ≤ cashback ≤ tributo. Renda zero/negativa, valores ausentes e tributos líquidos negativos são rejeitados; não há descarte silencioso. Se a dissertação adotar outra convenção, adapte o método antes de comparar. Registre as exclusões e a parcela populacional afetada.

## Indicadores e decisões metodológicas

* Carga por décimo: 100 × soma ponderada do tributo / soma ponderada da renda. Não é média dos quocientes individuais.
* Redução: carga antes menos carga depois, em pontos percentuais.
* Gini: coeficiente de concentração da renda ordenada por ela própria.
* Kakwani: concentração do tributo ordenado por renda menos Gini da renda pré-tributação. Valores negativos indicam regressividade relativa; positivos, progressividade. Se o tributo agregado for zero, o índice é indefinido (`null`).
* Pesos: posições fracionárias ponderadas, com empates de renda agrupados. Décimos têm exatamente 10% da massa ponderada, dividindo proporcionalmente grupos que cruzam os limites. Isso pode diferir de comandos que alocam cada observação integralmente a um décimo.
* O Kakwani é calculado nas observações, não aproximado por dez médias. Não mede, sozinho, a redução efetiva da desigualdade pós-tributação.
* Estimativas pontuais: o módulo não calcula erros-padrão nem incorpora estratos e unidades primárias de amostragem para inferência.

Referência para a convenção K = C − G: [World Bank, Fiscal incidence, inequality and poverty](https://documents1.worldbank.org/curated/en/110551607400316887/pdf/Burkina-Faso-Fiscal-incidence-Inequality-and-Poverty.pdf).

## Da POF ao cenário

Este módulo começa após harmonizar os microdados. Para reproduzir a dissertação, documente: arquivos e versão da POF; unidades de consumo e pessoas; códigos de despesas; tratamento de aquisições não monetárias; deflatores e anualização; renda e pesos; incidência tributária por item; classificação da cesta básica; elegibilidade; formalização e adesão; devolução; hipóteses de preços e comportamento. Nenhuma alíquota nem regra legal é imposta pelo programa.

Uma alteração na cesta básica muda a construção de `tax_before`; não pode ser simulada corretamente apenas subtraindo cashback. Para comparar cenários de cesta básica, execute o módulo em bases construídas para cada cenário, mantendo população e conceitos comparáveis.

## Validação

Os testes verificam Gini conhecido, proporcionalidade, imposto uniforme regressivo, cashback focalizado, empates, invariância à escala dos pesos, imposto líquido zero e rejeição de entradas inválidas. Eles validam o módulo, não a especificação empírica da dissertação.

## Pesquisa

[Portfólio](https://lftcontreras.github.io/) · [LinkedIn](https://www.linkedin.com/in/luisfelipecontreras/) · [ORCID](https://orcid.org/0009-0009-0387-0558)

## Painel interativo

Cinco abas: visão geral, distribuição e cashback, comparação de cenários, dados e exportação e metodologia. Inclui oito gráficos: carga por décimo, Kakwani, alívio em pontos percentuais, redução relativa, perfil da carga, composição do tributo inicial e duas comparações entre cenários.

Use **Explorar exemplo fictício** para conhecer os gráficos sem carregar dados. O exemplo não contém estimativas empíricas nem Kakwani calculado. Para pesquisa, carregue o JSON do módulo. Guarde até quatro cenários na aba de comparação; a população, periodicidade e conceitos precisam ser comparáveis. O painel não permite combinar o exemplo marcado como fictício com arquivos sem essa marcação.

A redução relativa é 100 × redução em pontos percentuais / carga inicial. Quando a carga inicial é zero, a razão fica indefinida. A composição mostra tributo líquido e devolvido como proporção do tributo inicial, não da renda. Não são calculados montantes, pobreza ou curvas de concentração a partir das dez cargas.

A aba de dados exporta CSV delimitado por ponto e vírgula (com metadados), JSON e impressão pelo navegador, que pode ser salva como PDF. Os arquivos importados e cenários guardados ficam apenas na memória local da página; recarregar limpa a sessão.
