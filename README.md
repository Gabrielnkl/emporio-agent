# Empório da Música — agente de atendimento

Protótipo em Python de um agente conversacional para apoiar o atendimento da loja. O modelo conversa com o cliente e escolhe ferramentas explícitas para consultar catálogo, pedidos e políticas.

## Configuração e execução

Requisitos: Python 3.10+ e uma chave da API da OpenAI.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e adicione sua chave da API
python -m src.main
```

`OPENAI_MODEL` pode ser definido no `.env` para trocar o modelo. O padrão é `gpt-6-luna`, escolhido por ser um modelo eficiente para tarefas focadas e com suporte a function calling. Não compartilhe nem faça commit do `.env`.

## Arquitetura

- **OpenAI Python SDK + Responses API**: um agente especializado atende em português. `src/agent/orchestrator.py` executa o loop de function calling no código da aplicação: envia a mensagem e os schemas, despacha cada chamada local, e devolve os resultados ao modelo para formular a resposta.
- **Function tools** em `src/agent/tools.py`: `search_catalog`, `check_order` e `search_store_policies`, descritas em JSON Schema com modo estrito. O prompt orienta quando consultar cada fonte e proíbe inventar dados dinâmicos.
- **Dados**: `src/database/connection.py` lê os CSVs usando a biblioteca padrão; `src/database/models.py` mapeia as linhas para registros tipados; e `src/database/repository.py` implementa as consultas. Os pedidos exigem número e nome completo do titular.
- **Histórico**: fica em memória durante a sessão CLI e é descartado ao sair. As chamadas usam `store=False`; a aplicação envia o histórico necessário em cada turno.
- **Políticas**: `src/knowledge/retrieval.py` seleciona respostas curadas a partir de `data/policies.pdf`, sem embeddings. Para o pequeno conjunto de regras deste desafio, essa abordagem é simples de auditar. Uma evolução poderia extrair e indexar o PDF e usar retrieval para documentos maiores.

Escolhi o SDK principal da OpenAI e a Responses API em vez do Agents SDK para deixar o ciclo do agente visível e fácil de explicar: o projeto define os schemas das funções, despacha chamadas conhecidas e devolve seus resultados. Isso reduz uma camada de abstração num protótipo pequeno. O modelo melhora a interpretação de linguagem natural e a formulação da resposta; fontes estruturadas continuam sendo responsáveis por preço, estoque e pedidos. Esse loop segue a documentação oficial de [function calling](https://developers.openai.com/api/docs/guides/function-calling).

## Limitações e suposições

- Os CSVs são um retrato estático fornecido para o desafio; estoque e status não são atualizados em tempo real.
- O agente pode consultar pedidos após conferir número e nome, mas isso não é autenticação suficiente para um serviço real. Em produção, a consulta deveria passar por uma API autenticada.
- As políticas relevantes foram transcritas em respostas curadas no código. Mudanças no PDF exigem atualizar essas regras.
- O roteamento é feito pelo modelo e pode escolher ferramenta incorretamente. O prompt exige consulta para fatos de negócio, mas um sistema de produção também precisaria de testes, monitoramento e regras de validação.
- O canal atual é CLI. Não há integração com WhatsApp, CRM ou sistema de pedidos.
- O projeto não contém testes automatizados neste primeiro incremento.

## Exemplos

As conversas de demonstração estão em [`examples/`](examples/). Elas cobrem busca de produtos, devolução, consulta de pedido e pergunta fora do escopo.

## Uso de assistente de código

O protótipo foi desenvolvido com auxílio do OpenAI Codex. Usei o assistente para estruturar a aplicação, integrar ferramentas com a Responses API e elaborar a documentação. As consultas continuam explícitas no código e os dados de origem são os materiais fornecidos no desafio.
